# Auto Harvest in Open-word Game Genshin Impact Report

## What's Genshin?

Genshin Impact is an action role-playing game developed and published by miHoYo. There are many ways the player may interact with the world. There are gliding, climbing, interacting with the NPCs, and fighting with minions and deities. It is an open world adventure game about the journey of the player who is trying to find his or her lost sibling. It is one of the most revenue generating mobile games in the history. It won many prices in gaming including the Nobel price in gaming – The Game Award for Best Mobile Game.

## The initiative of the project

In this game, different resources should be collected to upgrade your characters and weapons. It could be quite tedious to collect those items. Also, different kinds of resources requires different methods of collection. For the most common resources you can find them directly in the environment and press F to collet. Also shown in the video, for some resources you need to use specific skills to collect. For other resources you need to use elemental reactions to collect.

## Implementation (version 1)

In the first implementation, we choose our model to be DQN. We defined our environment to be the following:

- states: realtime image from the game.
- action: going forward, leftward, rightward, and downward.
- reward: inverse of the relative distance on the screen of the character with respect with the nearest target (if there is no target found, the reward is 0). [TODO]

### Problems

1. The character may enter into states that cannot be solved by the defined actions. For example, the character might encounter enemies in the environment, and can only be resolved with a fight.
1. The training process has hardly any improvement. We suspect the reason is because directly inputting the entire 1920X1080 picture into the DQN.

## Implementation (version 2)

To counter the issue that the states of the environment is too large to train, we chose to first process the high level image input into low-level data. We changed our model to be a two-stage model. The image of the game is first passed through YoloX. Then, we are able to get the low-level data:  the coordinates of the bounding box surrounding each detected object and the name of the detected object. Then, we passed the low-level data into the DQN. In this model, We defined our environment to be the following:

- states: bounding boxes and names of the detected objects.
- action: going forward, leftward, rightward, and downward.
- reward: inverse of the relative distance on the screen of the character with respect with the nearest target (if there is no target found, the reward is 0).
- reset: when it reaches some number of steps (hyperparameter). 

### Problems

1. Sometimes the YoloX would lose trace of the character because there could be bushes that blocks the view.