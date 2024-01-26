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
