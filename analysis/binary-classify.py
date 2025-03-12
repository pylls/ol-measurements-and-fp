#!/usr/bin/env python3
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils import data
from datetime import datetime
import argparse
import os

args = argparse.ArgumentParser()
args.add_argument("dataset1", help="first dataset")
args.add_argument("dataset2", help="second dataset")
args.add_argument("-l", "--length", help="length of the traces", type=int, default=5000)
args.add_argument(
    "-ow",
    "--open-world",
    type=float,
    default=0.0,
    help="open world mode with given train split probability",
)
args = args.parse_args()

BATCH_SIZE = 128
EPOCHS = 200
FOLDS = 10


def update_dataset(name, filename, labels, dataset, tags, LENGTH=5000):
    npz = np.load(filename, allow_pickle=True)
    # labels in the npz file is uuid -> tag
    t = npz["labels"].item()
    tags.update(t)
    # update labels to uuid -> name
    for uuid in t:
        labels[uuid] = name
    d = npz["dataset"].item()
    for uuid in d:
        # base data is always 5000 long, since vanilla DF expects that
        data = np.zeros((1, 5000), dtype=np.float32)
        n = min(LENGTH, d[uuid].shape[1])
        data[0, :n] = d[uuid][0, :n]
        d[uuid] = data

    dataset.update(d)


def main():
    global BATCH_SIZE
    if not os.path.exists(args.dataset1):
        print(f"{args.dataset1} does not exist")
        return
    if not os.path.exists(args.dataset2):
        print(f"{args.dataset2} does not exist")
        return

    # labels is uuid -> label
    # dataset is uuid -> extracted trace
    # tags is uuid -> tag
    labels, dataset, tags = {}, {}, {}
    update_dataset(0, args.dataset1, labels, dataset, tags, args.length)
    dataset1_len = len(labels)
    update_dataset(1, args.dataset2, labels, dataset, tags, args.length)
    dataset2_len = len(labels) - dataset1_len

    assert len(labels) == len(dataset) == len(tags)
    print(
        f"{now()} loading datasets done, {len(labels)} samples, {dataset1_len} from {args.dataset1}, {dataset2_len} from {args.dataset2}"
    )
    base_accuracy = max(dataset1_len, dataset2_len) / len(labels)
    print(f"{now()} baseline accuracy {base_accuracy:.4f}")

    print(f"{now()} using DF with {args.length} cells")

    if args.open_world > 1.0:
        print(f"{now()} invalid train split probability {args.open_world}")
        return
    if args.open_world > 0.0:
        print(
            f"{now()} 'OPEN WORLD' MODE: splitting by tag, training probability {args.open_world}"
        )

    results = []

    print(
        f"{now()} training with {EPOCHS} epochs, batch size {BATCH_SIZE}, patience 10"
    )
    if torch.cuda.is_available():
        print(f"{now()} using {torch.cuda.get_device_name(0)}")
    print(f"{now()} we do {FOLDS}-fold cross validation with a 8:1:1 split")
    for k in range(FOLDS):
        print(f"{now()} running fold {k}...")

        # train, validation, test lists with uuids
        train, valid, test = [], [], []

        if args.open_world > 0.0:
            print(f"{now()} using open world mode, stratified by tag")
            # split by tag
            for tag in set(tags.values()):
                uuids = [uuid for uuid in tags if tags[uuid] == tag]

                # with some probability, add all uuids to train, else test
                if np.random.rand() < args.open_world:
                    train.extend(uuids)
                else:
                    test.extend(uuids)

        else:
            print(f"{now()} using closed world mode, stratified by label")
            # random split, 80% train, 10% validation, 10% test, stratified by label
            for label in set(labels.values()):
                uuids = [uuid for uuid in labels if labels[uuid] == label]
                np.random.shuffle(uuids)
                train.extend(uuids[: int(len(uuids) * 0.8)])
                valid.extend(uuids[int(len(uuids) * 0.8) : int(len(uuids) * 0.9)])
                test.extend(uuids[int(len(uuids) * 0.9) :])

        print(f"{now()} train {len(train)}, valid {len(valid)}, test {len(test)}")

        results.append(run_df(train, valid, test, dataset, labels, tags))

    accuracy = [r[0] for r in results]
    fpr = [r[1] for r in results]

    print(f"{now()} done, {FOLDS}-fold cross validation results")
    print(
        f"{now()} accuracy mean: {np.mean(accuracy):.4f}, std: {np.std(accuracy):.4f}"
    )
    print(f"{now()} fpr mean: {np.mean(fpr):.4f}, std: {np.std(fpr):.4f}")


def run_df(train, valid, test, dataset, labels, tags):
    model = DF(2)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    if torch.cuda.is_available():
        model.cuda()

    train_gen = data.DataLoader(
        Dataset(train, dataset, labels),
        batch_size=BATCH_SIZE,
        shuffle=True,
        drop_last=True,
    )

    optimizer = torch.optim.Adamax(params=model.parameters())
    criterion = torch.nn.CrossEntropyLoss()
    best_loss = float("inf")
    patience = 10

    for epoch in range(EPOCHS):
        # training
        model.train()
        torch.set_grad_enabled(True)
        running_loss = 0.0
        n = 0
        for x, Y in train_gen:
            x, Y = x.to(device), Y.to(device)
            optimizer.zero_grad()
            outputs = model(x)
            loss = criterion(outputs, Y)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            n += 1
        if running_loss < best_loss:
            best_loss = running_loss
            patience = 10
        else:
            patience -= 1
            if patience == 0:
                print("\tearly stopping, patience 10 reached")
                break

    # testing
    testing_gen = data.DataLoader(
        Dataset(test, dataset, labels), batch_size=BATCH_SIZE, drop_last=True
    )
    model.eval()
    torch.set_grad_enabled(False)
    predictions = []
    p_labels = []
    for x, Y in testing_gen:
        x = x.to(device)
        outputs = model(x)
        index = F.softmax(outputs, dim=1).data.cpu().numpy()
        predictions.extend(index.tolist())
        p_labels.extend(Y.data.numpy().tolist())
    predictions = np.array(predictions)
    p_labels = np.array(p_labels)

    # we made predictions, stored in the predictions array, and true labels in p_labels
    fp = 0
    tp = 0
    fn = 0
    tn = 0
    for i in range(len(predictions)):
        predicted = np.argmax(predictions[i])
        correct = p_labels[i]
        if predicted == 0 and correct == 1:
            fp += 1
        elif predicted == 0 and correct == 0:
            tp += 1
        elif predicted == 1 and correct == 0:
            fn += 1
        elif predicted == 1 and correct == 1:
            tn += 1
        else:
            print(f"{now()} unexpected prediction {predicted} for {correct}")

    fpr = fp / (fp + tn)
    tpr = tp / (tp + fn)
    fnr = fn / (fn + tp)
    tnr = tn / (tn + fp)
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    print(f"{now()} fold fpr {fpr:.4f}, tpr {tpr:.4f}, fnr {fnr:.4f}, tnr {tnr:.4f}")

    return (accuracy, fpr)


# from https://github.com/Xinhao-Deng/Website-Fingerprinting-Library/blob/master/WFlib/models/DF.py
class ConvBlock(nn.Module):
    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size,
        stride,
        pool_size,
        pool_stride,
        dropout_p,
        activation,
    ):
        super(ConvBlock, self).__init__()
        padding = (
            kernel_size // 2
        )  # Calculate padding to keep the output size same as input size
        # Define a convolutional block consisting of two convolutional layers,
        # each followed by batch normalization and activation
        self.block = nn.Sequential(
            nn.Conv1d(
                in_channels,
                out_channels,
                kernel_size,
                stride,
                padding=padding,
                bias=False,
            ),  # First convolutional layer
            nn.BatchNorm1d(out_channels),  # Batch normalization layer
            activation(inplace=True),  # Activation function (e.g., ELU or ReLU)
            nn.Conv1d(
                out_channels,
                out_channels,
                kernel_size,
                stride,
                padding=padding,
                bias=False,
            ),  # Second convolutional layer
            nn.BatchNorm1d(out_channels),  # Batch normalization layer
            activation(inplace=True),  # Activation function
            nn.MaxPool1d(
                pool_size, pool_stride, padding=0
            ),  # Max pooling layer to downsample the input
            nn.Dropout(p=dropout_p),  # Dropout layer for regularization
        )

    def forward(self, x):
        # Pass the input through the convolutional block
        return self.block(x)


# from https://github.com/Xinhao-Deng/Website-Fingerprinting-Library/blob/master/WFlib/models/DF.py
class DF(nn.Module):
    def __init__(self, num_classes, num_tab=1):
        super(DF, self).__init__()

        # Configuration parameters for the convolutional blocks
        filter_num = [32, 64, 128, 256]  # Number of filters for each block
        kernel_size = 8  # Kernel size for convolutional layers
        conv_stride_size = 1  # Stride size for convolutional layers
        pool_stride_size = 4  # Stride size for max pooling layers
        pool_size = 8  # Kernel size for max pooling layers
        length_after_extraction = (
            18  # Length of the feature map after the feature extraction part
        )

        # Define the feature extraction part of the network using a sequential
        # container with ConvBlock instances
        self.feature_extraction = nn.Sequential(
            ConvBlock(
                1,
                filter_num[0],
                kernel_size,
                conv_stride_size,
                pool_size,
                pool_stride_size,
                0.1,
                nn.ELU,
            ),  # Block 1
            ConvBlock(
                filter_num[0],
                filter_num[1],
                kernel_size,
                conv_stride_size,
                pool_size,
                pool_stride_size,
                0.1,
                nn.ReLU,
            ),  # Block 2
            ConvBlock(
                filter_num[1],
                filter_num[2],
                kernel_size,
                conv_stride_size,
                pool_size,
                pool_stride_size,
                0.1,
                nn.ReLU,
            ),  # Block 3
            ConvBlock(
                filter_num[2],
                filter_num[3],
                kernel_size,
                conv_stride_size,
                pool_size,
                pool_stride_size,
                0.1,
                nn.ReLU,
            ),  # Block 4
        )

        # Define the classifier part of the network
        self.classifier = nn.Sequential(
            nn.Flatten(),  # Flatten the tensor to a vector
            nn.Linear(
                filter_num[3] * length_after_extraction, 512, bias=False
            ),  # Fully connected layer
            nn.BatchNorm1d(512),  # Batch normalization layer
            nn.ReLU(inplace=True),  # ReLU activation function
            nn.Dropout(p=0.7),  # Dropout layer for regularization
            nn.Linear(512, 512, bias=False),  # Fully connected layer
            nn.BatchNorm1d(512),  # Batch normalization layer
            nn.ReLU(inplace=True),  # ReLU activation function
            nn.Dropout(p=0.5),  # Dropout layer for regularization
            nn.Linear(512, num_classes),  # Output layer
        )

    def forward(self, x):
        # Pass the input through the feature extraction part
        x = self.feature_extraction(x)

        # Pass the output through the classifier part
        x = self.classifier(x)

        return x


class Dataset(data.Dataset):
    def __init__(self, ids, dataset, labels):
        self.ids = ids
        self.dataset = dataset
        self.labels = labels

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, index):
        ID = self.ids[index]
        return self.dataset[ID], self.labels[ID]


def now():
    return datetime.now().strftime("%H:%M:%S")


if __name__ == "__main__":
    main()
