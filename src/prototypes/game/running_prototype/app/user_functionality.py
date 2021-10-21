import random

LEFT = ["admiring", "adoring", "affectionate", "agitated", "amazing", "angry", "awesome", "beautiful", "blissful",
		"bold", "boring", "brave", "busy", "charming", "clever", "cool", "compassionate", "competent", "condescending",
		"confident", "cranky", "crazy", "dazzling", "determined", "distracted", "dreamy", "eager", "ecstatic", "elastic",
		"elated", "elegant", "eloquent", "epic", "exciting", "fervent", "festive", "flamboyant", "focused", "friendly",
		"frosty", "funny", "gallant", "gifted", "goofy", "gracious", "great", "happy", "hardcore", "heuristic", "hopeful",
		"hungry", "infallible", "inspiring", "interesting", "intelligent", "jolly", "jovial", "keen", "kind", "laughing",
		"loving", "lucid", "magical", "mystifying", "modest", "musing", "naughty", "nervous", "nice", "nifty", "nostalgic",
		"objective", "optimistic", "peaceful", "pedantic", "pensive", "practical", "priceless", "quirky", "quizzical",
		"recursing", "relaxed", "reverent", "romantic", "sad", "serene", "sharp", "silly", "sleepy", "stoic", "strange",
		"stupefied", "suspicious", "sweet", "tender", "thirsty", "trusting", "unruffled", "upbeat", "vibrant", "vigilant",
		"vigorous", "wizardly", "wonderful", "xenodochial", "youthful", "zealous", "zen"]

RIGHT = ["albattani", "allen", "almeida", "antonelli", "agnesi", "archimedes", "ardinghelli", "aryabhata", "austin",
	"babbage", "banach", "banzai", "bardeen", "bartik", "bassi", "beaver", "bell", "benz", "bhabha", "bhaskara",
	"black", "blackburn", "blackwell", "bohr", "booth", "borg", "bose", "bouman", "boyd", "brahmagupta", "brattain",
	"brown", "buck", "burnell", "cannon", "carson", "cartwright", "carver", "cerf", "chandrasekhar", "chaplygin",
	"chatelet", "chatterjee", "chebyshev", "cohen", "chaum", "clarke", "colden", "cori", "cray", "curran", "curie",
	"darwin", "davinci", "dewdney", "dhawan", "diffie", "dijkstra", "dirac", "driscoll", "dubinsky", "easley", "edison",
	"einstein", "elbakyan", "elgamal", "elion", "ellis", "engelbart", "euclid", "euler", "faraday", "feistel", "fermat",
	"fermi", "feynman", "franklin", "gagarin", "galileo", "galois", "ganguly", "gates", "gauss", "germain", "goldberg",
	"goldstine", "goldwasser", "golick", "goodall", "gould", "greider", "grothendieck", "haibt", "hamilton", "haslett",
	"hawking", "hellman", "heisenberg", "hermann", "herschel", "hertz", "heyrovsky", "hodgkin", "hofstadter", "hoover",
	"hopper", "hugle", "hypatia", "ishizaka", "jackson", "jang", "jemison", "jennings", "jepsen", "johnson", "joliot",
	"jones", "kalam", "kapitsa", "kare", "keldysh", "keller", "kepler", "khayyam", "khorana", "kilby", "kirch", "knuth",
	"kowalevski", "lalande", "lamarr", "lamport", "leakey", "leavitt", "lederberg", "lehmann", "lewin", "lichterman",
	"liskov", "lovelace", "lumiere", "mahavira", "margulis", "matsumoto", "maxwell", "mayer", "mccarthy", "mcclintock",
	"mclaren", "mclean", "mcnulty", "mendel", "mendeleev", "meitner", "meninsky", "merkle", "mestorf", "mirzakhani",
	"montalcini", "moore", "morse", "murdock", "moser", "napier", "nash", "neumann", "newton", "nightingale", "nobel",
	"noether", "northcutt", "noyce", "panini", "pare", "pascal", "pasteur", "payne", "perlman", "pike", "poincare",
	"poitras", "proskuriakova", "ptolemy", "raman", "ramanujan", "ride", "ritchie", "rhodes", "robinson", "roentgen",
	"rosalind", "rubin", "saha", "sammet", "sanderson", "satoshi", "shamir", "shannon", "shaw", "shirley", "shockley",
	"shtern", "sinoussi", "snyder", "solomon", "spence", "stonebraker", "sutherland", "swanson", "swartz", "swirles",
	"taussig", "tereshkova", "tesla", "tharp", "thompson", "torvalds", "tu", "turing", "varahamihira", "vaughan",
	"visvesvaraya", "volhard", "villani", "wescoff", "wilbur", "wiles", "williams", "williamson", "wilson", "wing",
	"wozniak", "wright", "wu", "yalow", "yonath", "zhukovsky"]


def set_default_user_name(entry, data):
	"""
	This function automatically creates a username if a new user is added to
	the db.
	@param entry: The data of the user
	@type entry: dict
	@param data: The mongo db
	@type data: object
	@return: The changed user data
	@rtype: dict
	"""
	user_names = list(data.find({"user_name": {"$exists": True, "$ne": ""}}, {'user_name': 1}))
	good_name = False
	new_name = ""
	while good_name is False:
		# Choose two random entries from the lists
		left = LEFT[random.randint(0, len(LEFT) - 1)]
		right = RIGHT[random.randint(0, len(RIGHT) - 1)]
		new_name = left + " " + right  # combine random words from the lists
		# make sure that the max length of the name is 23 characters
		if len(new_name) < 23:
			if len(user_names) != 0:
				for x in user_names:  # check if username already exists
					good_name = True
					if x['user_name'] == new_name:
						break
			else:
				good_name = True

	entry['user_name'] = new_name
	return entry


def query_statistics(user_id, data, data_list):
	"""
	Provides the numerical data for the user statistics
	@param user_id: The id of the user
	@type user_id: String
	@param data: The mongo db
	@type data: object
	@param data_list: The dict containing all the listed queries
	@type data_list: dict
	@return: Dictionary containing the numbers of solved queries of the different categories and
			level
	@rtype: dict
	"""
	user = data.find_one({'_id': user_id})
	played_health_games_squid = user['queries']['health']['num_successful_queries'][0]
	played_health_games_chameleon = user['queries']['health']['num_successful_queries'][1]
	played_health_games = played_health_games_squid + played_health_games_chameleon

	played_personal_games_squid = user['queries']['personal']['num_successful_queries'][0]
	played_personal_games_chameleon = user['queries']['personal']['num_successful_queries'][1]
	played_personal_games = played_personal_games_squid + played_personal_games_chameleon

	played_crime_games_squid = user['queries']['crime']['num_successful_queries'][0]
	played_crime_games_chameleon = user['queries']['crime']['num_successful_queries'][1]
	played_crime_games = played_crime_games_squid + played_crime_games_chameleon

	played_law_games_squid = user['queries']['law']['num_successful_queries'][0]
	played_law_games_chameleon = user['queries']['law']['num_successful_queries'][1]
	played_law_games = played_law_games_squid + played_law_games_chameleon

	played_politics_games_squid = user['queries']['politics']['num_successful_queries'][0]
	played_politics_games_chameleon = user['queries']['politics']['num_successful_queries'][1]
	played_politics_games = played_politics_games_squid + played_politics_games_chameleon

	played_knowledge_games_squid = user['queries']['knowledge']['num_successful_queries'][0]
	played_knowledge_games_chameleon = user['queries']['knowledge']['num_successful_queries'][1]
	played_knowledge_games = played_knowledge_games_squid + played_knowledge_games_chameleon

	played_games_data = {'health': [played_health_games_squid, played_health_games_chameleon, played_health_games,
									len(data_list['queries']['health']) - 1],
						 'personal': [played_personal_games_squid, played_personal_games_chameleon,
									  played_personal_games, len(data_list['queries']['personal']) - 1],
						 'law': [played_law_games_squid, played_law_games_chameleon, played_law_games,
								 len(data_list['queries']['law']) - 1],
						 'crime': [played_crime_games_squid, played_crime_games_chameleon, played_crime_games,
								   len(data_list['queries']['crime']) - 1],
						 'politics': [played_politics_games_squid, played_politics_games_chameleon,
									  played_politics_games, len(data_list['queries']['politics']) - 1],
						 'knowledge': [played_knowledge_games_squid, played_knowledge_games_chameleon,
									   played_knowledge_games, len(data_list['queries']['knowledge']) - 1]
						 }
	return played_games_data
