# Instagram Spider
Scrapy spider used for saving all the photos and videos from an Instagram account without using Instagram API.

## Requirements :
- Python 3
- Scrapy

## Usage
To use this spider,
make sure that you have Python and Scrapy installed,
then use the following command :

```python
scrapy runspider instagram_spider.py -a account=<name of the account> -a videos=<y or n> -a timestamp=<y or n>
```

If you don't precise those parameters, they will be asked when you launched the spider.

All the photos and videos will be saved in folder with the name of the account.
The timestamp parameter allow you to automatically add the date at beginning of the folder's name.

### Options
You can use the --nolog option to avoid all the printed scrapy logs, or --loglevel ERROR to only display the important ones.

#### Notes
If you have trouble calling scrapy after installing it with pip3, try to replace the scrapy command by :

```python
python -m scrapy.cmdline
```
