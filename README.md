# Web Scrapping Repository

This repository is for learning how do webscraping in multiple ways.


# Setting up Conda environment
Navigate to this directory. Then do the following

```bash
conda env create -f env.yml
```

# Setting up Selenium
For help setting up the selenium driver for google chrome. Use this video https://www.youtube.com/watch?v=NB8OceGZGjA

## Instructions to update chrome
It is easier if you make sure chrome is the most up-to-date version

1. On your computer, open Chrome.
2. At the top right, click More .
3. Click Help. About Google Chrome.
4. Click Update Google Chrome. Important: If you can't find this button, you're on the latest version.
5. Click Relaunch.

## Instructions to download the selenium driver
After updating, we need to download the correct chrome driver from this website.

1. Go to `https://sites.google.com/chromium.org/driver/`
2. Click on **`the Chrome for Testing availability dashboard`**
3. Click on the **`Stable`** verison. This will take you to the stable version table
4. Find **`chromedriver`** row for your system. Then copy the link and paste into the browser. This will download a `.zip` file
5. Place this `.zip` file in the directory you are working from and Extract it there.
6. Copy the `chromedriver.exe` to the root directory you are working from.
7. You can then delete the original folder and the `.zip`

Your root directory should now contain:
- `example_data`
- `.gitignore`
- `chromedriver.exe`
- `env.yml`
- `main.py`
- `README.md`
