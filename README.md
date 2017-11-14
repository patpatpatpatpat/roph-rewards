# roph-rewards
Scripts for claiming free items from [Ragnarok Online Philippines](https://www.ragnarokonline.com.ph/news) website events.
Get the free items from their website:
 1. Without using the browser to login
 2. Without playing games or waiting 5 minutes to play the game again
 3. Without sharing anything to Facebook

## Requirements
### MacOS
1. Python 3.4+
2. `pip install robobrowser`

### Windows
1. Download & install Python 3.4+ here: https://www.python.org/downloads/windows/
2. When installing Python, be sure to check the "Add Python to the Windows Path" option
3. Open Windows command prompt, run `pip install robobrowser`

## Usage
1. Download the latest release here: https://github.com/patpatpatpatpat/roph-rewards/releases
2. Open `credentials.py`, replace `yourusername` and `yourpassword` with your actual ROPH username and password. Add more dictionaries if you have multiple accounts.
3. Using the terminal/command prompt, switch to the directory where you downloaded the roph-rewards project.
4. Run the script: `python roph_events.py`
5. If you have an item code, run `python roph_events.py <your_item_code>`.
   * Example: `python roph_events.py FEWY-DD9V-EZZ1-KA1G`

### Sample MacOS run
![Sample MacOS run](https://github.com/patpatpatpatpat/roph-rewards/blob/master/sample_runs/roph-rewards-mac.gif "Sample MacOS run")
### Sample Windows run
![Sample Windows run](https://github.com/patpatpatpatpat/roph-rewards/blob/master/sample_runs/roph-rewards-windows.gif "Sample Windows run")

## IMPORTANT NOTES
1. Be sure you are alone when using the scripts, since your username & password are hard-coded in the file.
2. The script won't work if you run it during server maintenance.
3. I try to create scripts as soon as new events are published. Check this page if new events are released.
4. Contributions are very welcome! Feel free to open a pull request.

## Past Events
| Event Name        | Start           | End  |
| ------------- |:-------------:| -----:|
| [Chaos Daily Login](https://www.ragnarokonline.com.ph/news/special-daily-login)      | September 27, 2017 (7.30 PM) | October 31, 2017 (11.59 PM) |
| [Let's Go To Hidden Novice Treasure's Adventure](https://www.ragnarokonline.com.ph/news/lets-go-hidden) | October 11, 2017 (4.00 PM) | November 8, 2017 (09.59 AM) |
| [Daily Login Rewards - October](https://www.ragnarokonline.com.ph/news/dailylogin-oct2017) | October 16, 2017 (04.00 PM) | November 14, 2017 (11.59 PM) |

## Supported ROPH Events
| Event Name        | Start           | End  |
| ------------- |:-------------:| -----:|
| Daily Login Rewards - December | November 15 , 2017 | December 14, 2017 (11.59 PM) |

