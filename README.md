<img src="https://images.fineartamerica.com/images/artworkimages/mediumlarge/3/grumman-lunar-module-artist-rendering-1965-aviation-history-archive.jpg" width="500">

# lunarlander

## Get started with

```sh
conda create -n <NAME> -c conda-forge python=3.10.*
conda activate <NAME>
git clone https://github.com/nvaytet/lunarlander
git clone https://github.com/<USERNAME>/<MYBOTNAME>_bot.git
cd lunarlander/
python -m pip install -e .
cd run/
ln -s ../../<MYBOTNAME>_bot .
python test.py
```
