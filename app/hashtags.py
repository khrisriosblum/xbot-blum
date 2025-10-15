
# Hashtag sets (deduplicated and curated as per spec)
SHEET1_HASHTAGS = [
    "#TechHouse", "#HouseMusic", "#ElectronicMusic", "#BalearicBeats", "#HouseGroove",
    "#ProducerLife", "#MusicProducer", "#StudioLife", "#MusicaElectronica",
    "#TechHouseSpain", "#ClubMusic", "#Underground"
]

SOUNDCLOUD_HASHTAGS = [
    "#DJ", "#DJLife", "#Traktor", "#PioneerDJ", "#Mixcloud",
    "#Ibiza", "#UndergroundHouse", "#MusicaElectronica", "#TechHouseSpain"
]

SPOTIFYTOPS_HASHTAGS = [
    "#TechHouse", "#HouseMusic", "#MinimalHouse", "#FunkyHouse", "#JackinHouse",
    "#UndergroundHouse", "#ElectronicMusic", "#HouseGroove", "#TechHouseSpain",
    "#ClubMusic", "#BalearicBeats"
]

# Recent-release extra tags (prepend if within RECENT_DAYS window)
RECENT_TAGS = {
    "sheet1": ["#NewMusic", "#OutNow", "#Beatport"],
    "soundcloud": ["#NowPlaying", "#SoundCloud", "#DJSet"],
    "spotifytops": ["#newcharts", "#playlist", "#spotify"],
}
