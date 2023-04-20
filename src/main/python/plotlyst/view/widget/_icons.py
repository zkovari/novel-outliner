"""
Plotlyst
Copyright (C) 2021-2023  Zsolt Kovari

This file is part of Plotlyst.

Plotlyst is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Plotlyst is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import string

people = [
    "fa5.angry", 'mdi.emoticon-angry', 'mdi.emoticon-neutral', "fa5.dizzy", "fa5.flushed", "fa5.frown",
    "fa5.frown-open", "fa5.grimace", "fa5.grin", "fa5.grin-alt", "fa5.grin-beam", 'mdi.emoticon', 'mdi.emoticon-cool',
    'mdi.emoticon-cool-outline', "fa5.grin-beam-sweat", "fa5.grin-hearts", "fa5.grin-squint", "fa5.grin-squint-tears",
    'mdi.emoticon-cry-outline', "fa5.grin-stars", "fa5.grin-tears", "fa5.grin-tongue", "fa5.grin-tongue-squint",
    'mdi.emoticon-devil', 'mdi.emoticon-devil-outline', "fa5.grin-tongue-wink", 'mdi.emoticon-wink',
    'mdi.emoticon-wink-outline', "fa5.grin-wink", "fa5.kiss", "fa5.kiss-beam", "fa5.kiss-wink-heart", "fa5.laugh",
    "fa5.laugh-beam", 'mdi.emoticon-kiss', 'mdi.emoticon-kiss-outline', 'mdi.emoticon-lol', 'mdi.emoticon-lol-outline',
    "fa5.laugh-squint", 'mdi.emoticon-tongue', 'mdi.emoticon-tongue-outline', "fa5.laugh-wink", "fa5.meh",
    'mdi.emoticon-sick', 'mdi.emoticon-sick-outline', "fa5.meh-blank", "fa5.meh-rolling-eyes", "fa5.sad-cry",
    "fa5.sad-tear", "fa5.smile", "fa5.smile-beam", "fa5.smile-wink", "fa5.surprise", "fa5.thumbs-down", "fa5.thumbs-up",
    "fa5.tired", "fa5.user", "fa5.user-circle", 'mdi.baby-face', 'mdi.baby-face-outline',

    "fa5s.address-book", "fa5s.address-card", "fa5s.allergies", "fa5s.angry", "fa5s.brain", "fa5s.hiking", "fa5s.baby",
    'mdi.human-pregnant', "fa5s.child", 'mdi.baby', 'mdi.human-baby-changing-table', 'mdi.human-cane', "fa5s.female",
    "fa5s.male", 'mdi.human-female', 'mdi.human-female-boy', 'mdi.human-female-girl', 'mdi.human-female-female',
    'mdi.human-handsdown', 'mdi.human-handsup', 'mdi.human-male', 'mdi.human-male-boy', 'mdi.human-male-child',
    'mdi.human-male-female', 'mdi.human-male-girl', 'mdi.human-male-male', "fa5s.people-carry", "fa5s.person-booth",
    "fa5s.portrait", "fa5s.pray", "fa5s.user-astronaut", "fa5s.user-friends", "fa5s.user-graduate", "fa5s.user-injured",
    "fa5s.user-lock", "fa5s.user-md", "fa5s.user-ninja", "fa5s.user-nurse", 'mdi.doctor', "fa5s.user-secret",
    "fa5s.user-shield", "fa5s.user-slash", "fa5s.user-tag", "fa5s.user-tie", "fa5s.users", "fa5s.users-cog",
    'mdi.account-cog', "fa5s.ice-cream", "mdi.account-cash", "mdi.account-check", "mdi.account-child",
    "mdi.account-child-circle", "mdi.account-child-outline", "mdi.account-cowboy-hat", "mdi.account-convert",
    "mdi.account-heart", "mdi.account-key", "mdi.account-hard-hat", "mdi.account-multiple", "mdi.account-reactivate",
    "mdi.account-plus", "mdi.account-reactivate-outline", "mdi.account-search", "mdi.account-star",
    "mdi.account-supervisor-circle", "mdi.account-switch", "mdi.account-tie", "mdi.account-voice", "mdi.beekeeper",
    "mdi.pirate", "mdi.ninja", "mdi.robber", "mdi.robot", "mdi.robot-angry", "mdi.robot-angry-outline",
    "mdi.robot-confused", "mdi.robot-confused-outline", "mdi.robot-dead", "mdi.robot-dead-outline", "mdi.robot-excited",
    "mdi.robot-excited-outline", "mdi.robot-happy", "mdi.robot-happy-outline", "mdi.robot-love",
    "mdi.robot-love-outline", "", "", "", "mdi.face-mask", "mdi.face-mask-outline", "mdi.face", "mdi.face-agent",
    "mdi.face-outline", "mdi.face-profile", "mdi.face-profile-woman", "mdi.face-recognition", "mdi.face-shimmer",
    "mdi.face-shimmer-outline", "mdi.face-woman", "mdi.face-woman-outline", "mdi.face-woman-shimmer",
    "mdi.face-woman-shimmer-outline", "mdi.offer", "mdi.hand", "mdi.hand-heart", "mdi.hand-heart-outline",
    "mdi.hand-okay", "mdi.hand-peace", "mdi.hand-peace-variant", "mdi.hand-pointing-down", "fa5s.diagnoses",
    "mdi.hand-wash",
    "mdi.hand-wash-outline", "mdi.hand-water", "mdi.handshake-outline", "mdi.head", "mdi.head-alert-outline",
    "mdi.head-heart-outline", "mdi.head-flash-outline", "mdi.head-lightbulb-outline", "", "mdi.mustache", "", "", "",
    "", "", "", "", "", "", "", "", "", "",
]

food = [
    "fa5s.apple-alt", 'mdi.food-apple-outline', "fa5s.bacon", 'mdi.noodles', "fa5s.bone", "fa5s.bread-slice",
    "mdi.bread-slice", "mdi.bread-slice-outline", "fa5s.candy-cane", "fa5s.carrot", 'mdi.fruit-cherries',
    'mdi.fruit-grapes', 'mdi.fruit-grapes-outline', 'mdi.fruit-pineapple', 'mdi.fruit-watermelon', 'mdi.peanut',
    'mdi.peanut-outline', "fa5s.cheese", 'mdi.cheese', 'mdi.food-croissant', "fa5s.cloud-meatball", 'mdi.pasta',
    "fa5s.cookie", 'mdi.cookie', 'mdi.cupcake', 'mdi.muffin', "fa5s.drumstick-bite", 'mdi.grill', "fa5s.egg", 'mdi.egg',
    'mdi.egg-easter', "fa5s.fish", 'mdi.fish', "fa5s.hamburger", 'mdi.food-drumstick', 'mdi.food-fork-drink',
    'mdi.food-variant', "fa5s.hotdog", 'mdi.food-turkey', "fa5s.ice-cream", 'mdi.ice-cream', 'mdi.ice-pop', "fa5s.leaf",
    'mdi.sausage', 'mdi.corn', 'mdi.pumpkin', "fa5s.lemon", "fa5s.pepper-hot", "fa5s.pizza-slice", "fa5s.seedling",
    "fa5s.stroopwafel", 'mdi.room-service', 'mdi.silverware', 'mdi.silverware-clean', 'mdi.silverware-fork-knife',
    'mdi.silverware-spoon', "fa5s.beer", "mdi.beer", "mdi.beer-outline", "fa5s.cocktail", "fa5s.coffee", "fa5s.flask",
    'mdi.flask', 'mdi.flask-empty', 'mdi.flask-outline', 'mdi.flask-round-bottom', 'mdi.flask-round-bottom-empty',
    'mdi.flask-round-bottom-empty-outline', 'mdi.flask-round-bottom-outline', "fa5s.glass-cheers", "fa5s.glass-martini",
    "fa5s.glass-martini-alt", "fa5s.glass-whiskey", "fa5s.mug-hot", "fa5s.wine-bottle", "fa5s.wine-glass",
    "fa5s.wine-glass-alt", "mdi.baguette", "mdi.bottle-tonic", "mdi.bottle-tonic-skull", "mdi.bottle-tonic-outline",
    "mdi.bottle-tonic-plus", "mdi.bottle-tonic-plus-outline", "mdi.bottle-tonic-skull-outline",
    "mdi.bottle-tonic-skull-outline", "mdi.bottle-wine", "mdi.bottle-wine-outline", "mdi.bowl", "mdi.bowl-mix", "", "",
    "mdi.bowl-mix-outline", "mdi.bowl-outline", "mdi.pot", "mdi.pot-mix", "mdi.pot-steam", "mdi.shaker",
    "", "", "", "", "", "", "", "",
    "", "", "", "", "",
    "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",

]

nature = [
    'msc.globe', 'fa5s.globe', 'mdi.globe-model',
    'mdi.nature', 'mdi.nature-people', "fa5.lemon", "fa5.moon", "fa5.snowflake", "fa5.sun", 'mdi.flower',
    'mdi.flower-outline', 'mdi.image-filter-vintage', 'mdi.image-filter-hdr', 'mdi.island', 'mdi.mushroom',
    'mdi.mushroom-outline', 'mdi.flower-poppy', 'mdi.flower-tulip', 'mdi.flower-tulip-outline', "fa5s.apple-alt",
    "mdi.bacteria", "mdi.bacteria-outline", "fa5s.bolt", "fa5s.bug", "fa5s.cat", 'mdi.cat', "fa5s.crow", "fa5s.dog",
    'mdi.dog', 'mdi.dog-side', 'mdi.dog-service', "fa5s.dove", "fa5s.dragon", 'mdi.bird', 'mdi.duck', 'mdi.rabbit',
    'mdi.sheep', 'mdi.shark-fin', 'mdi.shark-fin-outline', "fa5s.feather", 'mdi.feather', "fa5s.feather-alt", 'mdi.owl',
    'mdi.penguin', "fa5s.fish", 'mdi6.fishbowl', 'mdi.snail', 'mdi.snake', 'mdi.tortoise', 'mdi.turtle',
    "fa5s.frog",
    "mdi.butterfly", "mdi.butterfly-outline", 'mdi.cow', 'mdi.pig', 'mdi.rodent', 'mdi.turkey', "fa5s.hippo",
    'mdi.elephant', 'mdi.kangaroo', 'mdi.koala', 'mdi.panda', "fa5s.horse", "fa5s.horse-head", 'mdi.horse',
    'mdi.horse-human', 'mdi.horse-variant', "fa5s.kiwi-bird", "fa5s.otter", 'mdi.donkey', 'mdi.jellyfish',
    'mdi.jellyfish-outline', 'mdi.ladybug', "fa5s.paw", "fa5s.spider", 'mdi.spider', 'mdi.spider-thread',
    'mdi.spider-web', "fa5s.tree", 'mdi.leaf-maple', 'mdi.cannabis', "fa5s.wind", 'mdi.campfire', "fa5s.mountain",
    'mdi.cloud', "fa5s.carrot", "fa5s.leaf", "fa5s.lemon", "fa5s.pepper-hot", "fa5s.seedling", "fa5s.water", "",
    "mdi.bat", "fa5s.cloud", "fa5s.cloud-meatball", "fa5s.cloud-moon", "fa5s.cloud-moon-rain", "fa5s.cloud-rain",
    "fa5s.cloud-showers-heavy", "fa5s.cloud-sun", "fa5s.cloud-sun-rain", "fa5s.meteor", "fa5s.moon", "fa5s.poo-storm",
    "fa5s.rainbow", "fa5s.smog", "fa5s.snowflake", "fa5s.sun", "fa5s.icicles", "fa5s.meteor", "fa5s.moon",
    "fa5s.pastafarianism", "mdi.barley", "mdi.bee", "mdi.bee-flower", "mdi.beehive-outline", "mdi.brightness-3", "", "",
    "mdi.cactus", "mdi.carrot", "mdi.hydro-power", "mdi.palm-tree", "mdi.unicorn", "mdi.unicorn-variant", "", "", "",
    "", "", "", "", "", "", "", "mdi.virus", "mdi.virus-outline", "", "", "", "", "", "", "", "", "", "", "", "", "",
    "",
    "", "", "", "", "", "", "", "", "", "", "", "",
    "", "", "", "",
    "", "", "", "", "", "", "", "", "", "", "", "",
    "", "", "", "", "", "", "", "", "", "", "", "",
    "", "", "", "",
]
sports = [
    "fa5.futbol", "fa5.life-ring", "fa5s.ambulance", "fa5s.baseball-ball", "fa5s.basketball-ball", "fa5s.bowling-ball",
    "fa5s.skating", "fa5s.skiing", 'mdi.ski', 'mdi.ski-cross-country', 'mdi.ski-water',
    "mdi.biathlon", "fa5s.skiing-nordic",
    "fa5s.snowboarding", 'mdi.curling',
    'mdi.fencing', "fa5s.running", 'mdi.cricket', "fa5s.skating", "fa5s.swimmer", "fa5s.swimming-pool", 'mdi.swim',
    "fa5s.walking",
    "fa5s.chess", "fa5s.chess-bishop", 'mdi.chess-bishop', "fa5s.chess-board", "fa5s.chess-king", 'mdi.chess-king',
    "fa5s.chess-knight", 'mdi.chess-knight', "fa5s.chess-pawn", 'mdi.chess-pawn', "fa5s.chess-queen", 'mdi.chess-queen',
    "fa5s.chess-rook", 'mdi.chess-rook',

    'mdi.dance-ballroom', 'mdi.dance-pole',

    "fa5s.gamepad", 'mdi.gamepad-variant', "fa5s.biking",
    "mdi.baseball-bat",
    "mdi.baseball", 'mdi.baseball-diamond', "mdi.basketball", "mdi.basketball-hoop",
    "mdi.basketball-hoop-outline", "mdi.bowling", "mdi.football", "mdi.football-australian", "mdi.football-helmet", "",
    "mdi.golf-tee", "mdi.golf", "mdi.karate", "", "",
    "mdi.roller-skate",
    "mdi.bike", "mdi.bike-fast", "mdi.billiards", "mdi.billiards-rack", "mdi.badminton", "mdi.handball", "mdi.hiking",
    "mdi.hockey-sticks", "mdi.hockey-puck", "mdi.polo",
    "mdi.pool", "mdi.racquetball",
    "mdi.rowing", "mdi.run", "mdi.soccer", "mdi.soccer-field",
    "mdi.volleyball", "mdi.water-polo", "", "", "", "", "", "", "", "", "", "",
    "", "", "", "", "", "", "", "", "", "", "", "",
    "", "", "", "",
    "", "", "", "", "", "", "", "", "", "", "", "",
    "", "", "", "", "", "", "", "", "", "", "", "",
    "", "", "", "",
]
places = [
    "fa5.building", "fa5.hospital", 'mdi.hospital-building', "fa5s.hospital-alt", 'mdi.bank', 'mdi.bank-outline',
    'mdi.castle', 'mdi.church', 'mdi.office-building', 'mdi.office-building-outline', 'mdi.routes',
    'mdi.city', 'mdi.city-variant', 'mdi.city-variant-outline', 'mdi.garage', 'mdi.garage-open', 'mdi.home',
    'mdi.home-city', 'mdi.home-group', 'mdi.home-heart', 'mdi.home-lightbulb', 'mdi.home-modern', 'mdi.home-outline',
    'mdi.home-roof', 'mdi.home-variant', 'mdi.home-variant-outline',
    'mdi.home-city-outline', 'mdi.home-flood', 'mdi.store', 'mdi.store-24-hour',
    'mdi.garage-open-variant', 'mdi.gate', 'mdi.gate-open',
    "mdi.bridge", 'mdi.factory', 'mdi.fuel',
    "fa5s.archway", "fa5s.baby-carriage", "fa5s.bath",
    "fa5s.bicycle", "fa5s.biking",
    "fa5s.tractor", 'mdi.dump-truck', 'mdi.forklift',
    "fa5s.igloo",
    "fa5s.snowplow", 'mdi.robot-mower', 'mdi.robot-mower-outline',
    'mdi.jeepney', 'mdi.rv-truck', 'mdi.tow-truck',
    "fa5s.tram", "fa5s.bus", "fa5s.bus-alt", "mdi.bus", "mdi.bus-alert", "mdi.bus-articulated-end", "mdi.bus-school",
    "mdi.bus-side", "mdi.bus-stop", 'mdi.bicycle', 'mdi.bicycle-basket', 'mdi.bicycle-electric',
    'mdi.bicycle-penny-farthing',
    'mdi.submarine', 'mdi.tank', 'mdi.tanker-truck',
    "fa5s.car", 'mdi.car', 'mdi.car-back', 'mdi.car-convertible', 'mdi.car-estate', 'mdi.car-hatchback', 'mdi.car-key',
    'mdi.car-lifted-pickup', 'mdi.car-limousine', 'mdi.car-pickup', 'mdi.car-seat', 'mdi.car-side', 'mdi.car-sports',
    'mdi.caravan',
    "fa5s.car-alt", "fa5s.car-crash",
    "fa5s.car-side", 'mdi.go-kart', 'mdi.golf-cart', 'mdi.gondola',
    'mdi.scooter', 'mdi.scooter-electric', 'mdi.human-scooter', 'mdi.human-wheelchair', "fa5s.fighter-jet",
    'mdi.parachute', 'mdi.parachute-outline', "fa5s.helicopter", 'mdi.fire-truck', "fa5s.motorcycle", 'mdi.motorbike',
    'mdi.motorbike-electric', 'mdi.baby-buggy', 'mdi.baby-carriage', 'mdi.baby-carriage-off', 'mdi.dolly',
    "mdi.air-purifier", "mdi.airbag", "mdi.airballoon", "mdi.airballoon-outline", "fa5s.plane", 'mdi.helicopter',
    "mdi.airplane", "mdi.airplane-landing", "mdi.airplane-off", "mdi.airplane-takeoff", "mdi.airport", "fa5s.rocket",
    'mdi.rocket', 'mdi.rocket-launch-outline', 'mdi.rocket-outline', "fa5s.ship", 'mdi.anchor', 'mdi.ferry',
    "fa5s.shopping-cart", "fa5s.shuttle-van", "fa5s.sleigh", "fa5s.space-shuttle", "fa5s.subway", 'mdi.subway',
    'mdi.subway-alert-variant', 'mdi.subway-variant', "fa5s.taxi", 'mdi.taxi', "fa5s.tractor", 'mdi.tractor',
    'mdi.tractor-variant', "fa5s.train", 'mdi.train', 'mdi.train-car', 'mdi.train-car-passenger',
    'mdi.train-car-passenger-door', 'mdi.train-car-passenger-door-open', 'mdi.train-car-passenger-variant',
    'mdi.train-variant', 'mdi.tram', "fa5s.tram", 'mdi.tram-side', "fa5s.truck", "fa5s.truck-monster", 'mdi.truck',
    'mdi.excavator', "fa5s.truck-pickup", "fa5s.wheelchair", "fa5s.traffic-light",
    "fa5s.clinic-medical", "fa5s.home", "fa5s.hotel", "fa5s.industry", "fa5s.mosque", "fa5s.vihara",
    "fa5s.place-of-worship", "fa5s.torii-gate", "fa5s.gopuram", "fa5s.synagogue", "mdi.barn", "mdi.beach",
    'mdi.tower-beach', 'mdi.tower-fire', 'mdi.ferris-wheel', "mdi.bag-carry-on", "mdi.bag-carry-on-check",
    "mdi.bag-carry-on-off", "mdi.bag-checked", "mdi.bag-personal", "mdi.bag-personal-off", "mdi.bag-suitcase",
    "mdi.earth", "mdi.eiffel-tower", "mdi.space-station",
]
objects = [
    'mdi.sword', 'mdi.sword-cross',
    'mdi.bell', 'mdi.candle', 'mdi.flashlight', 'mdi.candycane', 'mdi.cash', 'mdi.cash-100', 'mdi.cart-variant',
    'mdi.cash-register', 'mdi.fountain', 'mdi.halloween', 'mdi.handcuffs', 'mdi.hanger', 'mdi.hook', 'mdi.kettle',
    'mdi.kettle-pour-over', 'mdi.lipstick', 'mdi.oar', 'mdi.ornament', 'mdi.ornament-variant', 'mdi.purse',
    'mdi.keg', 'mdi.kettlebell', 'mdi.key', 'mdi.key-chain', 'mdi.key-chain-variant',
    "fa5.calendar", "fa5.calendar-alt", "fa5.clock", "fa5.compass", 'fa5s.map-signs', 'fa5s.scroll',
    'mdi.script', 'mdi.script-outline', 'mdi.script-text', 'mdi.script-text-key', 'mdi.script-text-key-outline',
    'mdi.script-text-outline', 'mdi.script-text-play',
    'mdi.telescope', 'mdi.test-tube',
    'mdi.stamper', 'mdi.typewriter',
    "fa5.envelope",
    "fa5.envelope-open", 'mdi.box-cutter', 'mdi.gift-open-outline', 'mdi.gift-outline', 'mdi.gift',
    'mdi.shield', 'mdi.shield-bug', 'mdi.shield-cross', 'mdi.shield-cross-outline', 'mdi.shield-key', 'mdi.shield-off',
    'mdi.shield-off-outline', 'mdi.shield-outline', 'mdi.shield-plus', 'mdi.shield-star', 'mdi.shield-star-outline',
    'mdi.shield-sun', 'mdi.shield-sun-outline',
    'mdi.shoe-ballet', 'mdi.shoe-cleat', 'mdi.shoe-formal', 'mdi.shoe-heel', 'mdi.shoe-sneaker',
    'mdi.cigar', 'mdi.crystal-ball', 'mdi.cube', 'mdi.gavel', 'mdi.hair-dryer', 'mdi.horseshoe', 'mdi.police-badge',
    'mdi.police-badge-outline', 'mdi.pokeball', 'mdi.poker-chip', 'mdi.rake',
    "fa5.gem", 'mdi.diamond-stone', "mdi.pickaxe", 'mdi.shovel', 'mdi.android-studio', 'mdi.crane', 'mdi.pier-crane',
    "fa5.hourglass", 'mdi.blender', "fa5.lightbulb", 'mdi.auto-fix', 'mdi.lifebuoy',
    'mdi.compass-rose', 'mdi.compass-outline',
    "fa5.map", "fa5.money-bill-alt", "fa5.newspaper", 'mdi.archive', 'mdi.battery', 'mdi.fishbowl',
    "fa5.paper-plane", "fa5.trash-alt",
    "mdi.calculator", 'mdi.abacus', 'mdi.pill', 'mdi.saxophone',
    "fa5s.air-freshener",
    "fa5s.anchor", 'mdi.anchor', "fa5s.ankh", "fa5s.archive", "fa5s.atlas", "fa5s.bacon", "fa5s.band-aid", "fa5s.bible",
    "fa5s.beer", 'mdi.glass-flute', 'mdi.glass-pint-outline', 'mdi.glass-mug', 'mdi.glass-cocktail', 'mdi.glass-tulip',
    'mdi.glass-wine',
    "fa5s.blender", 'mdi.ladder',
    "fa5s.cocktail", "fa5s.coffee", 'mdi.baby-bottle', 'mdi.baby-bottle-outline',
    "fa5s.flask", 'mdi.cup', 'mdi.cup-water',
    "fa5s.glass-cheers", "fa5s.glass-martini", "fa5s.glass-martini-alt", "fa5s.glass-whiskey",
    "fa5s.mug-hot", "fa5s.wine-bottle", "fa5s.wine-glass", "fa5s.wine-glass-alt",
    "fa5s.binoculars",
    "mdi.binoculars",
    "mdi.camera", "mdi.camera-account", 'mdi.audio-video', 'mdi.audio-video-off', 'mdi.camcorder', "mdi.camera-enhance",
    "mdi.camera-enhance-outline", 'mdi.cassette',
    "mdi.camera-gopro", "mdi.camera-wireless", 'mdi.cellphone-basic', 'mdi.cellphone', 'mdi.disc', 'mdi.disc-player',
    'mdi.headphones', 'mdi.phone', 'mdi.phone-alert', 'mdi.phone-cancel', 'mdi.phone-check', 'mdi.phone-classic',
    'mdi.air-horn',
    "fa5s.birthday-cake", "mdi.cake", "mdi.cake-layered", "mdi.cake-variant",

    'mdi.cards', 'mdi.domino-mask',

    'mdi.pistol', 'mdi.knife', 'mdi.knife-military', 'mdi.saw-blade', "fa5s.bomb", "fa5s.bone", "fa5s.bong",
    "fa5s.book", "fa5s.book-dead", "fa5s.book-medical", 'mdi.bandage', 'mdi.barrel', 'mdi.fire-extinguisher',
    'mdi.fire-hydrant', 'mdi.firework', 'mdi.fireplace', 'mdi.fireplace-off', 'mdi.boomerang', "fa5s.book-open",
    'mdi.bookshelf', "fa5s.box", "fa5s.box-open", "fa5s.bread-slice", "fa5s.briefcase", 'mdi.briefcase',
    'mdi.briefcase-variant-outline', "fa5s.briefcase-medical", 'mdi.medical-bag', "fa5s.broom", "mdi.broom",
    "fa5s.brush", "mdi.brush", "fa5s.wine-bottle", 'mdi.coat-rack', "mdi.bucket", "mdi.bucket-outline", 'mdi.bugle',
    'mdi.fridge', "fa5s.umbrella", 'mdi.umbrella', 'mdi.umbrella-closed-variant', 'mdi.umbrella-outline',
    'mdi.umbrella-closed', "fa5s.mitten", "fa5s.journal-whills", "fa5s.robot", "fa5s.satellite", "fa5s.satellite-dish",
    "mdi.bullet", 'mdi.coffin', "fa5s.dice", "fa5s.dice-one", "fa5s.dice-two", "fa5s.dice-three", "fa5s.dice-four",
    "fa5s.dice-five", "fa5s.dice-six", "fa5s.dice-d6", "fa5s.dice-d20", "fa5s.cubes", "fa5s.cube", "fa5s.hammer",
    "fa5s.brush", "fa5s.drafting-compass", "fa5s.dumpster", "fa5s.hard-hat", 'mdi.bullhorn', "fa5s.paint-roller",
    'mdi.tooth', 'mdi.tooth-outline', 'mdi.toothbrush', 'mdi.toothbrush-electric', 'mdi.toothbrush-paste', 'mdi.torch',
    "fa5s.pencil-alt", "fa5s.pencil-ruler", "fa5s.ruler", "fa5s.ruler-combined", "fa5s.ruler-horizontal",
    "fa5s.ruler-vertical", "fa5s.screwdriver", 'mdi.nail', 'mdi.screw-flat-top', 'mdi.screw-lag', 'mdi.screw-round-top',
    'mdi.screwdriver', "fa5s.toolbox", 'mdi.hammer', 'mdi.tools', "fa5s.tools", "fa5s.wrench", "fa5s.guitar",
    'mdi.guitar-acoustic', 'mdi.anvil', 'mdi.cog', 'mdi.cogs', 'mdi.hammer-screwdriver', 'mdi.hammer-wrench',
    'mdi.spade', "fa5s.hamburger", "fa5s.hanukiah", "fa5s.hard-hat", "fa5s.hat-wizard", 'mdi.wizard-hat',
    "fa5s.highlighter", "fa5s.oil-can", "fa5s.piggy-bank", "fa5s.cookie", "fa5s.cookie-bite", "fa5s.mask",
    "mdi.lighthouse", "mdi.lighthouse-on", "",

    "fa5s.tv", 'mdi.antenna', "fa5s.bed", 'mdi.seat', 'mdi.seat-flat', 'mdi.seat-individual-suite', 'mdi.sofa',
    'mdi.sofa-outline', 'mdi.sofa-single', "mdi.bed", "mdi.bed-double", "mdi.bed-double-outline", "mdi.bed-empty",
    "mdi.bed-king", "mdi.bed-king-outline", "mdi.bed-outline", "mdi.bed-queen", "mdi.bed-queen-outline",
    "mdi.bed-single", "mdi.bed-single-outline", 'mdi.desk', 'mdi.desk-lamp', 'mdi.floor-lamp', 'mdi.floor-lamp-dual',
    'mdi.lamp', 'mdi.lamps', 'mdi.deskphone', 'mdi.desktop-classic', 'mdi.desktop-mac', 'mdi.desktop-mac-dashboard',
    'mdi.desktop-tower-monitor', "mdi.balloon", "mdi.basket", "mdi.bone", "mdi.bomb", "mdi.bolt", "mdi.bow-tie", "", "",
]

characters = [
    "mdi.null", "mdi.numeric", "mdi.numeric-0", "mdi.numeric-1", "mdi.numeric-2", "mdi.numeric-3", "mdi.numeric-4",
    "mdi.numeric-5", "mdi.numeric-6", "mdi.numeric-7", "mdi.numeric-8", "mdi.numeric-9", "mdi.numeric-10",
    "mdi.numeric-0-box", "mdi.numeric-1-box", "mdi.numeric-2-box", "mdi.numeric-3-box", "mdi.numeric-4-box",
    "mdi.numeric-5-box", "mdi.numeric-6-box", "mdi.numeric-7-box", "mdi.numeric-8-box", "mdi.numeric-9-box",
    "mdi.numeric-10-box",

    "mdi.numeric-0-box-outline", "mdi.numeric-1-box-outline", "mdi.numeric-2-box-outline", "mdi.numeric-3-box-outline",
    "mdi.numeric-4-box-outline", "mdi.numeric-5-box-outline", "mdi.numeric-6-box-outline", "mdi.numeric-7-box-outline",
    "mdi.numeric-8-box-outline", "mdi.numeric-9-box-outline", "mdi.numeric-10-box-outline", "mdi.numeric-0-circle",
    "mdi.numeric-1-circle", "mdi.numeric-2-circle", "mdi.numeric-3-circle", "mdi.numeric-4-circle",
    "mdi.numeric-5-circle", "mdi.numeric-6-circle", "mdi.numeric-7-circle", "mdi.numeric-8-circle",
    "mdi.numeric-9-circle", "mdi.numeric-10-circle", "mdi.numeric-0-circle-outline", "mdi.numeric-1-circle-outline",
    "mdi.numeric-2-circle-outline", "mdi.numeric-3-circle-outline", "mdi.numeric-4-circle-outline",
    "mdi.numeric-5-circle-outline", "mdi.numeric-6-circle-outline", "mdi.numeric-7-circle-outline",
    "mdi.numeric-8-circle-outline", "mdi.numeric-9-circle-outline", "mdi.numeric-10-circle-outline",

    "mdi.numeric-0-box-multiple", "mdi.numeric-1-box-multiple", "mdi.numeric-2-box-multiple",
    "mdi.numeric-3-box-multiple", "mdi.numeric-4-box-multiple", "mdi.numeric-5-box-multiple",
    "mdi.numeric-6-box-multiple", "mdi.numeric-7-box-multiple", "mdi.numeric-8-box-multiple",
    "mdi.numeric-9-box-multiple", "mdi.numeric-10-box-multiple", "mdi.numeric-0-box-multiple-outline",
    "mdi.numeric-1-box-multiple-outline", "mdi.numeric-2-box-multiple-outline", "mdi.numeric-3-box-multiple-outline",
    "mdi.numeric-4-box-multiple-outline", "mdi.numeric-5-box-multiple-outline", "mdi.numeric-6-box-multiple-outline",
    "mdi.numeric-7-box-multiple-outline", "mdi.numeric-8-box-multiple-outline", "mdi.numeric-9-box-multiple-outline",
    "mdi.numeric-10-box-multiple-outline",

    "mdi.numeric-9-plus", "mdi.numeric-9-plus-box", "mdi.numeric-9-plus-box-multiple",
    "mdi.numeric-9-plus-box-multiple-outline", "mdi.numeric-9-plus-box-outline", "mdi.numeric-9-plus-circle",
    "mdi.numeric-9-plus-circle-outline", "mdi.numeric-negative-1",

    'mdi.roman-numeral-1', 'mdi.roman-numeral-2', 'mdi.roman-numeral-3', 'mdi.roman-numeral-4', 'mdi.roman-numeral-5',
    'mdi.roman-numeral-6', 'mdi.roman-numeral-7', 'mdi.roman-numeral-8', 'mdi.roman-numeral-9', 'mdi.roman-numeral-10',

    "mdi.alpha", 'mdi.beta', 'mdi.omega',
    'mdi.alphabet-aurebesh', 'mdi.alphabet-cyrillic', 'mdi.alphabet-greek',
    'mdi.alphabet-latin',
    'mdi.alphabet-piqad', 'mdi.alphabet-tengwar', 'mdi.alphabetical', 'mdi.alphabetical-off',
    'mdi.alphabetical-variant', 'mdi.book-alphabet'
]

for char in list(string.ascii_lowercase):
    characters.append(f'mdi.alpha-{char}')
for char in list(string.ascii_lowercase):
    characters.append(f'mdi.alpha-{char}-box')
for char in list(string.ascii_lowercase):
    characters.append(f'mdi.alpha-{char}-box-outline')
for char in list(string.ascii_lowercase):
    characters.append(f'mdi.alpha-{char}-circle')
for char in list(string.ascii_lowercase):
    characters.append(f'mdi.alpha-{char}-circle-outline')

symbols = [
    'fa5s.yin-yang', 'mdi.all-inclusive', 'mdi.christianity', 'mdi.drama-masks', 'mdi.flag', 'mdi.flag-triangle',
    'mdi.flag-checkered', 'mdi.license', 'mdi.power-sleep', 'mdi.pulse',
    "fa5.bell", "fa5.bell-slash", "fa5.comment", "fa5.copyright", "fa5.comments", "fa5.comment-dots",
    "fa5.dot-circle", "fa5.eye", "fa5.eye-slash", 'mdi.pin',
    'mdi.heart', 'mdi.heart-broken', 'mdi.heart-broken-outline', 'mdi.heart-circle', 'mdi.heart-circle-outline',
    'mdi.heart-box', 'mdi.heart-box-outline', 'mdi.heart-cog', 'mdi.heart-cog-outline', 'mdi.heart-flash',
    'mdi.heart-half', 'mdi.heart-half-full', 'mdi.heart-half-outline', 'mdi.heart-multiple',
    'mdi.heart-multiple-outline', 'mdi.heart-pulse',
    "fa5.heart", "fa5s.heart-broken", "fa5s.heartbeat", 'mdi.calendar-heart', 'mdi.battery-heart',
    'mdi.battery-heart-variant', 'mdi.sparkles',
    "fa5.image", "fa5.images", "fa5.question-circle",
    "fa5.registered", "fa5.star", "mdi.brain", 'mdi.creation',
    "fa5.star-half", "fa5s.adjust", 'mdi.one-up',
    "mdi.bullseye", "mdi.bullseye-arrow", 'mdi.deathly-hallows', 'mdi.death-star', 'mdi.death-star-variant',
    'mdi.klingon', 'mdi.opacity',
    "fa5s.american-sign-language-interpreting",
    "fa5s.asterisk", "fa5s.at", 'mdi.fingerprint',
    'mdi.orbit', 'mdi.smoking', 'mdi.smoking-off', 'mdi.smoking-pipe', 'mdi.smoking-pipe-off', "fa5s.atom",
    "fa5s.battery-empty", "fa5s.battery-full", "fa5s.battery-half", "fa5s.battery-quarter",
    "fa5s.battery-three-quarters", "fa5s.broadcast-tower", "fa5s.burn", "fa5s.charging-station", "fa5s.fan", 'mdi.fan',
    "fa5s.fire", "fa5s.fire-alt", 'mdi.fire', 'mdi.fire-alert', "fa5s.gas-pump", "fa5s.radiation", "fa5s.radiation-alt",
    'mdi.radioactive', 'mdi.radioactive-off', "fa5s.solar-panel", 'mdi.history',

    'mdi.music', 'mdi.music-clef-treble', 'mdi.music-note', 'mdi.music-note-half', "mdi.account-music",
    "mdi.account-music-outline", 'mdi.puzzle', 'mdi.puzzle-check', 'mdi.puzzle-check-outline', 'mdi.puzzle-heart',
    "fa5s.lira-sign", 'mdi.pig-variant', 'mdi.pig-variant-outline', 'mdi.piggy-bank', "fa5s.money-bill",
    "fa5s.money-bill-alt", "fa5s.money-bill-wave", "fa5s.money-bill-wave-alt", "fa5s.money-check",
    "fa5s.money-check-alt", "fa5s.pound-sign", "fa5s.ruble-sign", "fa5s.rupee-sign", "fa5s.shekel-sign", "fa5s.tenge",
    "fa5s.won-sign", "fa5s.yen-sign", 'mdi.currency-usd', 'mdi.currency-twd', 'mdi.currency-bdt', 'mdi.currency-brl',
    'mdi.currency-btc', 'mdi.currency-cny', 'mdi.currency-eth', 'mdi.currency-eur', 'mdi.currency-eur-off',
    'mdi.currency-gbp', 'mdi.currency-ils', 'mdi.currency-inr', 'mdi.currency-jpy', 'mdi.currency-krw',
    'mdi.currency-kzt', 'mdi.currency-mnt', 'mdi.currency-ngn', 'mdi.currency-php', 'mdi.currency-rial',
    'mdi.currency-rub', 'mdi.currency-sign', 'mdi.currency-try', 'mdi.bell-alert', 'mdi.bell-alert-outline',
    'mdi.bell-cancel', 'mdi.bell-cancel-outline', 'mdi.bell-check', 'mdi.bell-circle', 'mdi.bell-sleep', 'mdi.cctv',
    'mdi.atom', 'mdi.atom-variant', "fa5s.award", 'mdi.medal', 'mdi.medal-outline', 'mdi.seal', 'mdi.seal-variant',
    'mdi.trophy', 'mdi.trophy-award', 'mdi.trophy-broken', 'mdi.trophy-outline', 'mdi.trophy-variant',
    'mdi.trophy-variant-outline', "fa5s.balance-scale", "fa5s.balance-scale-left", "fa5s.balance-scale-right",
    "fa5s.ban", "fa5s.biohazard", "mdi.biohazard", 'mdi.chemical-weapon', 'mdi.nuke', "fa5s.blind", "fa5s.braille",
    "fa5s.temperature-high", "fa5s.temperature-low", "fa5s.restroom", "fa5s.hand-spock", "fa5s.jedi", "fa5s.hashtag",
    "", "", "fa5s.icons", "fa5s.infinity", "fa5s.info", "fa5s.info-circle", "fa5s.shapes", "fa5s.dollar-sign",
    "fa5s.euro-sign", "fa5s.hryvnia",

    'mdi.middleware', 'mdi.middleware-outline',
    "fa5s.angle-double-down", "fa5s.angle-double-left", "fa5s.angle-double-right", "fa5s.angle-double-up",
    "fa5s.angle-down", "fa5s.angle-left", "fa5s.angle-right", "fa5s.angle-up", "fa5s.arrow-alt-circle-down",
    "fa5s.arrow-alt-circle-down", "fa5s.arrow-alt-circle-left", "fa5s.arrow-alt-circle-left",
    "fa5s.arrow-alt-circle-right", "fa5s.arrow-alt-circle-right", "fa5s.arrow-alt-circle-up",
    "fa5s.arrow-alt-circle-up", "fa5s.arrow-circle-down", "fa5s.arrow-circle-left", "fa5s.arrow-circle-right",
    "fa5s.arrow-circle-up", "fa5s.arrow-down", "fa5s.arrow-left", "fa5s.arrow-right", "fa5s.arrow-up",
    "fa5s.arrows-alt", "fa5s.arrows-alt-h", "fa5s.arrows-alt-v", 'mdi.arrow-decision-auto-outline',
    'mdi.arrow-decision', 'mdi.arrow-horizontal-lock', "fa5s.caret-down", "fa5s.caret-left", "fa5s.caret-right",
    "fa5s.caret-square-down", "fa5s.caret-square-down", "fa5s.caret-square-left", "fa5s.caret-square-left",
    "fa5s.caret-square-right", "fa5s.caret-square-right", "fa5s.caret-square-up", "fa5s.caret-square-up",
    "fa5s.caret-up", "fa5s.cart-arrow-down", "fa5s.chart-line", "fa5s.chevron-circle-down", "fa5s.chevron-circle-left",
    "fa5s.chevron-circle-right", "fa5s.chevron-circle-up", "fa5s.chevron-down", "fa5s.chevron-left",
    "fa5s.chevron-right", "fa5s.chevron-up", "fa5s.cloud-download-alt", "fa5s.cloud-upload-alt",
    "fa5s.compress-arrows-alt", "fa5s.download", "fa5s.exchange-alt", "fa5s.expand-arrows-alt",
    "fa5s.external-link-alt", "fa5s.external-link-square-alt", "fa5s.hand-point-down", "fa5s.hand-point-down",
    "fa5s.hand-point-left", "fa5s.hand-point-left", "fa5s.hand-point-right", "fa5s.hand-point-right",
    "fa5s.hand-point-up", "fa5s.hand-point-up", "fa5s.hand-pointer", "fa5s.hand-pointer", "fa5s.allergies",
    "fa5s.fist-raised", "fa5s.hand-holding", "fa5s.hand-holding-heart", "fa5s.hand-holding-usd", "fa5s.hand-lizard",
    "fa5s.hand-middle-finger", "fa5s.hand-paper", "fa5s.hand-peace", "fa5s.hand-rock", "fa5s.hand-scissors",
    "fa5s.hand-spock", "fa5s.hands", "fa5s.hands-helping", "fa5s.handshake", "fa5s.praying-hands", "fa5s.thumbs-down",
    "fa5s.thumbs-down", "fa5s.thumbs-up", "fa5s.thumbs-up",

    "fa5s.history", "fa5s.level-down-alt", "fa5s.level-up-alt", "fa5s.location-arrow", "fa5s.long-arrow-alt-down",
    "fa5s.long-arrow-alt-left", "fa5s.long-arrow-alt-right", "fa5s.long-arrow-alt-up", "fa5s.mouse-pointer",
    "fa5s.play", "fa5s.random", "fa5s.recycle", "fa5s.redo", "fa5s.redo-alt", "fa5s.reply", "fa5s.reply-all",
    "fa5s.retweet", "fa5s.share", "fa5s.share-square", "fa5s.share-square", "fa5s.sign-in-alt", "fa5s.sign-out-alt",
    "fa5s.sort", "fa5s.sort-alpha-down", "fa5s.sort-alpha-down-alt", "fa5s.sort-alpha-up", "fa5s.sort-alpha-up-alt",
    "fa5s.sort-amount-down", "fa5s.sort-amount-down-alt", "fa5s.sort-amount-up", "fa5s.sort-amount-up-alt",
    "fa5s.sort-down", "fa5s.sort-numeric-down", "fa5s.sort-numeric-down-alt", "fa5s.sort-numeric-up",
    "fa5s.sort-numeric-up-alt", "fa5s.sort-up", "fa5s.sync", "fa5s.sync-alt", "fa5s.text-height", "fa5s.text-width",
    "fa5s.undo", "fa5s.undo-alt", "fa5s.upload",

    'mdi.gender-female', 'mdi.gender-male', 'mdi.gender-male-female', 'mdi.gender-male-female-variant',
    'mdi.gender-non-binary', 'mdi.gender-transgender', "fa5s.genderless", "fa5s.mars", "fa5s.mars-double",
    "fa5s.mars-stroke", "fa5s.mars-stroke-h", "fa5s.mars-stroke-v", "fa5s.mercury", "fa5s.neuter", "fa5s.transgender",
    "fa5s.transgender-alt", "fa5s.venus", "fa5s.venus-double", "fa5s.venus-mars",

    "fa5s.ghost", "fa5s.skull-crossbones", 'mdi.skull', 'mdi.skull-crossbones', 'mdi.skull-crossbones-outline',
    'mdi.skull-outline', 'mdi.skull-scan', 'mdi.skull-scan-outline',
    "fa5s.tint", "fa5s.tint-slash", "fa5s.infinity", "fa5s.peace",

    "fa5s.bullseye", "fa5s.check-circle", "fa5s.circle", "fa5s.dot-circle", "fa5s.microphone", "fa5s.microphone-slash",
    "fa5s.star", "fa5s.star-half", "fa5s.star-half-alt", "fa5s.toggle-off", "fa5s.toggle-on", "fa5s.wifi",

    "mdi.alarm", "mdi.alarm-bell", "mdi.alarm-check", "mdi.alarm-light", "mdi.alarm-light-outline",
    "mdi.alarm-multiple", "mdi.alarm-note", "mdi.alarm-note-off", "mdi.alarm-off", "mdi.alarm-plus", "mdi.alarm-snooze",
    "mdi.album", "mdi.alert", "mdi.alert-box", "mdi.alert-box-outline", "mdi.alert-circle", "mdi.alert-circle-check",
    "mdi.alert-circle-check-outline", "mdi.alert-circle-outline", "mdi.alert-decagram", "mdi.alert-decagram-outline",
    "mdi.alert-octagon", "mdi.alert-octagon-outline", "mdi.alert-octagram", "mdi.alert-octagram-outline",
    "mdi.alert-outline", "mdi.alert-rhombus", "mdi.alert-rhombus-outline", "mdi.alien", "mdi.alien-outline",

    "mdi.allergy", "mdi.arm-flex", "mdi.arm-flex-outline",
]

icons_registry = {
    'People': people,
    'Food': food,
    'Animals & Nature': nature,
    'Sports & Activities': sports,
    'Travel & Places': places,
    'Objects': objects,
    'Numbers and Characters': characters,
    'Symbols': symbols,
}
