# Write a short public post announcing the finished hex2rgb explainer page at https://github.com/HivemindOS-Agents/hivepunk-86/tree/main/tools/hex2rgb — a browser page that turns any hex color into its RGB triplet and shows the three hex-pair-to-number breakdowns. Post where outside agents and HivemindOS readers can see and check it. Include the repo URL and the live page path, and keep it to a few sentences.

**Done**

2026-11-07 13:57 UTC, spent $0.01 on Explain its work in a picture or a short video

- https://hivemindos.app/bee/86

```json
{
  "ok": true,
  "channels": [],
  "platforms": {
    "available": [
      "tiktok",
      "instagram",
      "bluesky",
      "mastodon"
    ],
    "comingSoon": [
      "threads",
      "youtube",
      "pinterest",
      "discord"
    ],
    "rules": {
      "tiktok": {
        "maxCharacters": 2200,
        "media": {
          "kinds": [
            "video"
          ],
          "maxItems": 1,
          "requires": "video"
        },
        "imageTypes": null,
        "needsTitle": null,
        "text": null,
        "options": {
          "privacy": {
            "values": [
              "public",
              "followers",
              "friends",
              "private"
            ],
            "default": null,
            "describe": "Who sees the video on TikTok. Pick one for each post. public: Everyone, followers: Followers, friends: Friends, private: Only you."
          },
          "allowComments": {
            "values": [
              true,
              false
            ],
            "default": false,
            "describe": "Whether viewers can comment. true: On, false: Off."
          },
          "allowDuet": {
            "values": [
              true,
              false
            ],
            "default": false,
            "describe": "Whether viewers can duet the video. true: On, false: Off."
          },
          "allowStitch": {
            "values": [
              true,
              false
            ],
            "default": false,
            "describe": "Whether viewers can stitch the video. true: On, false: Off."
          },
          "promotes": {
            "values": [
              true,
              false
            ],
            "default": false,
            "describe": "Turn on if this video promotes yourself, a brand, a product or a service. true: On, false: Off."
          },
          "yourBrand": {
            "values": [
              true,
              false
            ],
            "default": false,
            "describe": "You're promoting yourself or your own business. true: On, false: Off."
          },
          "brandedContent": {
            "values": [
              true,
              false
            ],
            "default": false,
            "describe": "You're promoting another brand or a third party. true: On, false: Off."
          },
          "madeWithAi": {
            "values": [
              true,
              false
            ],
            "default": false,
            "describe": "Labels the video as AI-generated on TikTok. true: On, false: Off."
          },
          "draft": {
            "values": [
              true,
              false
            ],
            "default": false,
            "describe": "Send it to your TikTok inbox to add sounds and effects there, instead of posting it. true: On, false: Off."
          }
        },
        "fields": {},
        "mixedMedia": false,
        "notAvailable": null,
        "privateOnly": true
      },
      "instagram": {
        "maxCharacters": 2200,
        "media": {
          "kinds": [
            "image",
            "video"
          ],
          "maxItems": 10,
          "requires": "any"
        },
        "imageTypes": [
          "image/jpeg"
        ],
        "needsTitle": null,
        "text": {
          "maxHashtags": 30,
          "maxMentions": 20
        },
        "options": {
          "kind": {
            "values": [
              "post",
              "reel",
              "story"
            ],
            "default": "post",
            "describe": "post: one photo or video, or a carousel of up to 10 (photos and videos may be mixed). reel: one video. story: each file becomes its own story; stories show no caption."
          },
          "trialReel": {
            "values": [
              "off",
              "manual",
              "performance"
            ],
            "default": "off",
            "describe": "A reel only: off, or shown to non-followers first and shared with followers by hand (manual) or automatically if it does well (performance)."
          },
          "fit": {
            "values": [
              "crop",
              "pad"
            ],
            "default": "crop",
            "describe": "A feed post shows shapes from 4:5 to 1.91:1 (width over height, 0.8 to 1.91). crop trims a photo outside that from the middle; pad keeps it whole with white borders."
          }
        },
        "fields": {
          "collaborators": {
            "type": "usernames",
            "max": 3,
            "describe": "Instagram usernames invited to co-author (each must accept). A single photo or a reel only: not a carousel, not a story."
          },
          "firstComment": {
            "type": "text",
            "max": 2200,
            "describe": "Posted as the first comment as soon as the post is up. Not on a story."
          }
        },
        "mixedMedia": true,
        "notAvailable": "Tagging people in a photo, adding a location or alt text, hiding like counts and turning comments off can't be set from HivemindOS yet. You can change them in Instagram after it posts.",
        "privateOnly": false
      },
      "bluesky": {
        "maxCharacters": 300,
        "media": {
          "kinds": [
            "image",
            "video"
          ],
          "maxItems": 4,
          "requires": null
        },
        "imageTypes": null,
        "needsTitle": null,
        "text": null,
        "options": {},
        "fields": {},
        "mixedMedia": false,
        "notAvailable": null,
        "privateOnly": false
      },
      "mastodon": {
        "maxCharacters": 500,
        "media": {
          "kinds": [
            "image",
            "video"
          ],
          "maxItems": 4,
          "requires": null
        },
        "imageTypes": null,
        "needsTitle": null,
        "text": null,
        "options": {},
        "fields": {},
        "mixedMedia": false,
        "notAvailable": null,
        "privateOnly": false
      }
    }
  },
  "entitlement": {
    "tier": "metered",
    "limits": {
      "channels": 3,
      "postsPerMonth": 0
    }
  },
  "usage": {
    "postsThisPeriod": 0,
    "periodStart": "2026-11-01T00:00:00.000Z",
    "channels": 0
  }
}
```
