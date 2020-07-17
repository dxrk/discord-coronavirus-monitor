# Discord Coronavirus Monitor

Track the latest using this discord monitor!

## Installation

Ensure to install packages before running using the following command.

```bash
pip install -r requirements.txt
```

## Usage

Update this information before running in the ``config.json`` file! Webhook relates to the Discord Webhook. If you are unsure what those are, please look [here](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).

A `refreshInterval` of `5` is recommended. Anything lower could be harmful to JHU.

### Description

**world**-  This module displays info for each country, but not any specific cities throughout the world.

**unitedStates**- This module displays individual US data per state.

**usSpecific**- This module displays US counties data. More specific than `unitedStates`.

**graphs**- Displays updates to the most up to date Covid-19 numbers.

![Chart Example](/bar_charts/example.png)

```json
{
    "monitor": true,
    "refreshInterval": 5,
    "imgurClientID": "",
    "usSpecific": {
        "enabled?": true,
        "webhookEnabled?": true,
        "webhook": ""
    },
    "unitedStates": {
        "enabled?": true,
        "webhookEnabled?": true,
        "webhook": ""
    },
    "world": {
        "enabled?": true,
        "webhookEnabled?": true,
        "webhook": ""
    },
    "graphs": {
        "hourly": {
            "enabled?": true,
            "webhook": ""
        },
        "daily": {
            "enabled?": true,
            "webhook": ""
        }
    }
}
```
If `enabled?` is set to `true`, the modules will be activated. They will only print to console unless `webhookEnabled?` is set to `true`. 

After config is completed, use the following command to start the monitor.

```bash
node main
```

## Retrieve imgurClientID 

In order to retrieve your `imgurClientID`, (*only needed if graphs is enabled*), ypu must create an application through imgur. Please follow the guide on how to do so [here](https://apidocs.imgur.com/?version=latest).

## Resources

- This monitor uses the Johns Hopkins database, (more specifically from the [arcgis.com](https://gisanddata.maps.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6) service).
- Discord webhooks are implemented for easy viewing purposes. **GRAPHS CAN ONLY BE SEEN ON DISCORD**
- Imgur used to upload graphs, but also stored in the `bar_graphs` folder.

## License
[MIT](https://choosealicense.com/licenses/mit/)
