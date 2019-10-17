# cryptotradingbot
A (very) lightweight cryptoasset MA crossover trading bot for Coinbase Pro.

My motivation for writing this was to combat excessive costs in a running a real-time trading bot. Constantly checking trade status, 
streaming real-time prices, calculating multiple metrics on the fly, and updating records can really start to addup in costs for a 
casual retail trader. The point of this script is to create a simple MA crossover trading bot that executes only as often as you want it to.

This script, with function parameters inserted at the bottom, should be set to always-on. It will only execute the functions every n seconds
that you input. 
