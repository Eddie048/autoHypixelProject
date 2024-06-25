# HypixelProject

This project has two primary functionalities. Firstly, given a minecraft username it can display information about how good the given player is at Hypixel Bedwars. This is determined based on their statistics taken from the Hypixel API. https://api.hypixel.net

Secondly, while running, it can detect screenshots being taken, so taking a screenshot while in game is detected automatically. It then uses a homemade image to text translater relying on Minecraft's pixelated font to get the usernames as strings. The other players' stats are then requested from the Hypixel API to find threatening players. Lastly, the system displays a desktop notification when done, with information about how threatening the players are.

To Use:

1. Download the packages from `requirements.txt`.
2. Change the name of `config_example.json` to `config.json`.
3. Change the default values in `config.json` .
   1. Create an API Key at https://developer.hypixel.net and add to the "api-key" field.
   2. Find your minecraft screenshots directory and add the full path to the "screenshots-directory" field. Note that your computer's screenshots and minecraft screenshots are saved to different places.
   3. Find your pixel_scale value, which is the number of pixels on your screen a pixel of minecraft text takes up. The easiest way to find this is take a screenshot of text in minecraft and count the width of a pixel in an image editor on your computer. Place this value in the "pixel_size" field.
   4. Add your username and any other usernames you want the tracker to ignore to the "ignored-usernames" field. This is just so you don't have your own data cluttering up the view, but it isn't necessary.
4. Run the program from `main.py`.
5. Join a bedwars lobby on hypixel.net.
6. Hold down the 'tab' key to make player's usernames visible at the top of your screen.
7. While holding the 'tab' key, take a screenshot, usually by pressing F2 or FN F2.
8. The results should appear in the terminal that you are running python in, and a notification will display.
9. Repeat if necessary.