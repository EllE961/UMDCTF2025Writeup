# Sunshine

## Challenge
> A local garbage truck was photographed in Summit County, Ohio with house number 356 visible in the background. For investigative purposes, we need to determine the full address. Can you find the exact location?

## Solution
For this challenge, I needed to find the full address of house number 356.

Given the hint about Summit County, Ohio, I used the public GIS server:
https://scgis.summitoh.net/hosted/rest/services/AddressPoints_DBC/FeatureServer

My approach:
1. Wrote a Python script to inspect available fields
2. Queried for addresses where `ADDR_NUM = '356'` and `CITY = 'AKRON'` (since the garbage truck had an Akron city sign)
3. Filtered through multiple results for the correct address

## Flag
`UMDCTF{356 Hillwood Dr, Akron, OH 44320}` 