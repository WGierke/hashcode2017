# hashcode2017
Heuristic Solution for Google Hash Code 2017

## Idea
- Per endpoint, calculate the average latency saving when a video could be put in cache
- Per endpoint and video, calculate the value of the video, which is *VideoRequests* \* *AverageSaving* / *VideoSize*
- Put videos with highest values first in endpoint caches

## Score
The solution achieved 1,521,626 points (~2,6M is currently the best score achieved by a team).
