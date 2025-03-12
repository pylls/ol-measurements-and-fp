echo "basic autoloc"
./binary-classify.py autoloc-100.npz clearnet-ol-0.npz
./binary-classify.py autoloc-100.npz onion-ol-0.npz

echo "curl"
./binary-classify.py curl-only-general.npz clearnet-only-general.npz

echo "open world"
./binary-classify.py autoloc-100.npz clearnet-ol-0.npz --open-world 0.8
./binary-classify.py autoloc-100.npz onion-ol-0.npz --open-world 0.8
./binary-classify.py autoloc-100.npz clearnet-ol-0.npz --open-world 0.5
./binary-classify.py autoloc-100.npz onion-ol-0.npz --open-world 0.5
./binary-classify.py autoloc-100.npz clearnet-ol-0.npz --open-world 0.3
./binary-classify.py autoloc-100.npz onion-ol-0.npz --open-world 0.3

echo "overlap"
./binary-classify.py autoloc-100.npz negative-ol-100.npz

echo "positive class limit"
./binary-classify.py autoloc-75.npz clearnet-ol-0.npz
./binary-classify.py autoloc-50.npz clearnet-ol-0.npz
./binary-classify.py autoloc-35.npz clearnet-ol-0.npz
./binary-classify.py autoloc-30.npz clearnet-ol-0.npz
./binary-classify.py autoloc-75.npz onion-ol-0.npz
./binary-classify.py autoloc-50.npz onion-ol-0.npz
./binary-classify.py autoloc-35.npz onion-ol-0.npz
./binary-classify.py autoloc-30.npz onion-ol-0.npz

echo "circuit fingerprinting"
./binary-classify.py clearnet-only-general.npz clearnet-no-general.npz -l 512
./binary-classify.py onion-only-hsdir.npz onion-no-hsdir.npz -l 512
./binary-classify.py onion-only-intro.npz onion-no-intro.npz -l 512
./binary-classify.py onion-only-rend.npz onion-no-rend.npz -l 512

