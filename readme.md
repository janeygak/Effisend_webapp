<snippet>
  <content>
# EffiSend Web App


Effisend is a webapp used to find the best rates for transferring money overseas. Users can look up rates based on their payment method or how fast funds need to be available. After a transfer, the user can then have Effisend send an SMS to the receiver with the amount and time funds will be available in their time zone. The app also gives users a conversion of their money into a familiar commodity in the destination country as a reference.

Using data from the World Bank, Effisend visualizes how much money is sent overseas as well as the cost of living in each country so users can understand how far their remittances will go.

## Screenshots

<img src="https://cloud.githubusercontent.com/assets/14094159/13935038/80ef5474-ef72-11e5-963c-f486afc707e6.png" height="20%" width="20%"> 

<img src="https://cloud.githubusercontent.com/assets/14094159/13935037/80ebc71e-ef72-11e5-9944-148378ded835.png" height="15%" width="15%">

<img src="https://cloud.githubusercontent.com/assets/14094159/13935036/80e78ac8-ef72-11e5-96c9-69e6e61ff618.png" height="15%" width="15%">

## Installation

Install the required libraries from the requirements.txt. 
Register an account at Twilio to use the send sms api.
Register an account at currency layer to use realtime currency exchange api.

Create a sql database called "money transfers" and run the models by typing "python model.py" in your terminal.

Run the server by typing "python server.py" in your terminal.

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D


## Credits

All rates and money transfer data come from the World Bank. The prices of rice and water are crowdsourced from Numbeo. The amount of rice a family can live off is from 
the World Food Program. 


</content>
</snippet>