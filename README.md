# Using a bot to do VoIP communication

I will document how to build a bot that does VoIP using the SIP protocol. If you're not clear on how SIP works, please have a read of [this link](https://www.voipmechanic.com/sip-basics.htm). 

Here's a video of the end result: [video](). It works with any SIP client - so if you happen to have a device that can take calls using SIP, then you'll be able to do this as well.

Here are the steps required:
- **Set up an SIP server.** I set up [Brekeke](http://wiki.brekeke.com/wiki/Brekeke-SIP-Server-v3-Quickstart) (free 60 day trial) in a Windows VM. However, there are always open source solutions that you can explore, such as [OVerSIP](http://oversip.net/).
- **Set up an SIP client, which will be your bot.** I used the [python wrapper for pjsip](https://trac.pjsip.org/repos/wiki/Python_SIP_Tutorial), which is an open source library. 
- **Set up Cognitive Services.** This will be used to understand the user's utterances.

## Setting up the SIP server

When you first [install Brekeke](http://wiki.brekeke.com/wiki/Brekeke-SIP-Server-v3-Quickstart), the interface IP address will be your local IP address. You need to add your public facing IP address by going to the Configuration page, then filling in the "Interface address 1" field with the public facing IP address of the VM. You'll need to go into the Azure Portal and configure the security rules for your VM as well to allow traffic from other SIP clients. 

You'll then need to add user accounts so that they can communicate through your server. Make sure the usernames are all numbers. To test that your server is working, install an SIP client app (e.g. AgePhone or CSipSimple) on 2 different phones. In each phone, put in the user credentials and IP address of the VM. You should then be able to call and chat with each other using the app.

## Setting up the SIP client

