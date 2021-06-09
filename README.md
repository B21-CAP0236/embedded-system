![20210609_120532](https://user-images.githubusercontent.com/18365721/121311910-0fc2c280-c92f-11eb-8071-23ed9e91bf79.jpg)

# **anANTara** embedded system

anANTara project relies mainly on the vending machine which built by this embedded system repository, this contains processes that are happening when a bansos recipient want to authenticate themselves to get social assistance.

However, we have not created the storage system yet because our main focus for the MVP is just the authentication system that is consisting of OCR and Facial Recognition system that already built in the machine learning submodule.

We also print the [3d model of the authentication system casing](./3d-model/anantara.stl), so everything are already setup in a good way and ready to rock, its just that we are currently lacking the storage sytem that makes the system not fully automated in case of sharing the social assistance itself, but its just a matter of time (and money) to create the storage system and make a fully automated vending machine that could be used for a "self-service social assistance sharing system".

## Feature(s)

These are features that available for embedded system part :

1. OCR System

   We use a [PiCamera](https://www.raspberrypi.org/products/camera-module-v2/) to scan the ID Card and crop certain region of interests and try to grab the text out of it and compare and match it with the data that already existed in the database (have been inputted by the admins). 
   
2. Face Recognition and Similarity System

   For this process, we use a webcam to capture the recipient's face for multiple times (5 times in this case), and try to compare it with the photo that already captured from the ID Card in the OCR process before, if all this comparison passes the threshold (we set it to 3 out of 5), then the recipient will be verified and is eligible for getting the social assistance.

3. GPS System

   We also track the location of this vending machine (just in case something bad happened like someone steal it from the bansos placement) adn update it in the database so all the admins that have the priviledge will be able to see and locate the real location of the vending machine itself.

4. Integration with the Cloud

   This vending machine is connected with the backend that exist in the cloud so for each and every transaction will be stored and updated in the backend to let admins and possibly all other people see who are getting the social assistance and track other informative data that could be collected and processed for further data processing

## Development

### Tech Stack (Software side)

- PyQt5 for showing all the UI system and connect it to all other components
- Machine Learning submodule (see [machine-learning repository](https://github.com/B21-CAP0236/machine-learning) for more detail on its tech stacks)
- Graphql Client to connect it with the graphql endpoint served by Hasura Cloud

### Tech Stack (Hardware side)

- [Raspberry Pi 4 RAM 8GB](https://www.tokopedia.com/snapshot_product?order_id=784427475&dtl_id=1224127180) for the whole processing unit
- [Raspberry Pi 4 - Metal Case Double Fan](https://www.tokopedia.com/snapshot_product?order_id=784427476&dtl_id=1224127182) to cool the raspberrypi
- [LCD 7 Inch 7" HDMI Touchscreen 1024x600 Raspberry Pi Display Monitor C](https://www.tokopedia.com/snapshot_product?order_id=784427477&dtl_id=1224127185) to show the UI and let the recipient interact with it
- [RGB KY-016 full 3 Color LED module KY016 arduino Raspberry](https://www.tokopedia.com/snapshot_product?order_id=789858396&dtl_id=1237623542) to light up the ID Card when scanning it
- [GPS MODULE Ublox NEO-6M Neo-6m-v2 Arduino](https://www.tokopedia.com/snapshot_product?order_id=784427474&dtl_id=1224127176) to track the location of the vending machine
- [Logitech Webcam C270 HD](https://www.tokopedia.com/goldenmouse/logitech-webcam-c270-hd-only-webcam-sja) to capture the recipient's face
- [Power Supply Adaptor Switching LED 12V 3A](https://www.tokopedia.com/snapshot_product?order_id=676702974&dtl_id=1010950084) to power up the DC FAN
- [FAN DC 12 VOLT 8x8x2.5CM](https://www.tokopedia.com/cncstorebandung/fan-dc-12-volt-8x8x2-5cm) to cool things up
- [Motor Servo Sg90](https://www.tokopedia.com/cncstorebandung/cnc-towerpro-motor-servo-sg90-sg-90-9g) to move the ID Card in or out (setting up for the cartridge mechanism)

### How to Contribute

These are steps that need to be done for development :
- Fork this repository
- Create issue in this repository about what problem you want to fix / what feature you want to add
- Start the development in your own repository by first creating branch that are unique to the development (problem to fix / feature to add)
- Open pull request to this repository and ask maintainer (anantara-embeddedsytem-team) that consist of [@fakhri](https://github.com/fakhrip) to review the PR
- Wait for the review approval and merge if approved

Or you can also contribute to this project by giving us donation and/or funding to develop this project further (you can contact [@fakhri](https://github.com/fakhrip) (my contact list is on [my website](https://justak.id)) or other members of this project)
