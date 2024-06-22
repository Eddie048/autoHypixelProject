# HypixelProject

This project has two primary functionalities. Firstly, given a minecraft username it can display information about how good the given player is at Hypixel Bedwars. This is determined based on their statistics taken from the Hypixel API. https://api.hypixel.net

Secondly, while running, it can detect screenshots being taken, so taking a screenshot while in game is detected automatically. It then uses a homemade image to text translater relying on Minecraft's pixelated font to get the usernames as strings. The other players' stats are then requested from the Hypixel API to find threatening players. Lastly, the system displays a desktop notification when done, with information about how threatening the players are.
