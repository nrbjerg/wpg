# WPG
Scripts for creating theme specific wallpapers, here are some screenshots:
![Random Walk](/screenshots/random_walk_onedark.png)
![Grid based approac](/screenshots/without_middles.PNG "Chained together, without middles")
# Usage
Clone the repository

``` sh
git clone https://github.com/nrbjerg/wpg
```
Edit the `config.py` file to your liking, and run 

``` sh
python random_walk.py
```
This will begin the process of coloring the canvas using a random walk, with the colores specified in the config, afterwards the remaining black pixels are removed, this mean that the color "#000000", cannot be used in the final product. This shouldn't take too long, afterwards a custom algorithm is ran to remove unessary noise, this algorithm is VERY slow, so be carefull when picking canvas sizes. Please note that the canvas can be scalled up, this however comes with the tradeoff that the final product will be more pixilated (Personally i like this, as a fan of pixel art.) :D, however feel free to contribute a better algorithm for removing the noise ;).
## Contributing
Feel free to clone and contribute what ever fetures you would like
