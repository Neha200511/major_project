"""
DEMO Training Dataset for Child Safety ML Classifier.

IMPORTANT: This is DEMO/SYNTHETIC data for model training and evaluation.
It does NOT contain real conversations. Real-world deployment requires
training on properly curated and ethically sourced datasets.

Categories: SAFE, BULLYING, THREAT, GROOMING, SELF_HARM, PRIVACY_RISK, MANIPULATION, SCAM
"""


def get_training_data():
    """Return list of (text, label) tuples for training."""
    training_data = [
        # ============================================================
        # SAFE - 160 samples
        # Includes examples that LOOK dangerous but aren't
        # ============================================================
        
        # Normal conversation
        ("How was your exam today?", "SAFE"),
        ("It was pretty good, I think I passed", "SAFE"),
        ("What homework do we have for tomorrow?", "SAFE"),
        ("Can you help me with the math homework?", "SAFE"),
        ("Sure, which problems are you stuck on?", "SAFE"),
        ("The algebra ones are really hard", "SAFE"),
        ("Let me explain it step by step", "SAFE"),
        ("Thanks that makes so much more sense now", "SAFE"),
        ("Are you coming to school tomorrow?", "SAFE"),
        ("Yeah I'll be there for first period", "SAFE"),
        ("What time does the bus come?", "SAFE"),
        ("Usually around 7:30 in the morning", "SAFE"),
        ("Good morning! Ready for the test?", "SAFE"),
        ("Not really, I stayed up late studying", "SAFE"),
        ("You'll do great, don't worry", "SAFE"),
        ("Thanks, I hope so", "SAFE"),
        ("What are you doing this weekend?", "SAFE"),
        ("Probably just hanging out at home", "SAFE"),
        ("We should study together for the final", "SAFE"),
        ("That's a great idea, when works for you?", "SAFE"),
        
        # Movie/Entertainment context (words that look dangerous but are safe)
        ("Did you watch the new Marvel movie?", "SAFE"),
        ("The villain killed everyone in that scene", "SAFE"),
        ("That fight scene was absolutely brutal", "SAFE"),
        ("The hero destroyed the entire city", "SAFE"),
        ("I loved when they killed the bad guy at the end", "SAFE"),
        ("The battle scene was so violent but cool", "SAFE"),
        ("Did you see the new horror movie? So scary!", "SAFE"),
        ("The monster killed like ten people in that scene", "SAFE"),
        ("That plot twist was killer dude", "SAFE"),
        ("This movie is going to blow your mind", "SAFE"),
        ("The action scenes were fire", "SAFE"),
        ("That Netflix show is insane", "SAFE"),
        ("The character died in the last episode", "SAFE"),
        ("I'm binge watching the whole series", "SAFE"),
        ("The anime fight was so epic", "SAFE"),
        ("Have you watched Stranger Things?", "SAFE"),
        ("That series finale was devastating", "SAFE"),
        ("The zombie scene was terrifying", "SAFE"),
        ("I can't believe they killed off my favorite character", "SAFE"),
        ("The new Star Wars movie has so many battles", "SAFE"),
        
        # Gaming context
        ("Want to play Minecraft later?", "SAFE"),
        ("I killed you in Fortnite haha", "SAFE"),
        ("We destroyed their team in the match", "SAFE"),
        ("Get rekt noob lol", "SAFE"),
        ("I'm going to destroy you in this game", "SAFE"),
        ("Let's attack their base together", "SAFE"),
        ("I died again on that level", "SAFE"),
        ("This boss fight is killing me", "SAFE"),
        ("We absolutely murdered them in that round", "SAFE"),
        ("I'll snipe you from across the map", "SAFE"),
        ("My kill streak was insane last game", "SAFE"),
        ("Let's blow up the enemy base", "SAFE"),
        ("I'm going to hunt you down in the game", "SAFE"),
        ("That was a sick headshot", "SAFE"),
        ("We need more players for our team", "SAFE"),
        ("What's your rank in Valorant?", "SAFE"),
        ("I finally beat the final boss!", "SAFE"),
        ("The new update for Roblox is awesome", "SAFE"),
        ("Can you join my Minecraft server?", "SAFE"),
        ("I crafted a diamond sword", "SAFE"),
        
        # Sports context
        ("We killed them in the football match", "SAFE"),
        ("That was a crushing defeat for the other team", "SAFE"),
        ("Our team destroyed theirs 5-0", "SAFE"),
        ("I'm going to beat you at basketball", "SAFE"),
        ("Did you see the fight in the hockey game?", "SAFE"),
        ("That tackle was absolutely brutal", "SAFE"),
        ("The pitcher is throwing fire today", "SAFE"),
        ("We demolished the opposing team", "SAFE"),
        ("Are you coming to practice tomorrow?", "SAFE"),
        ("Coach was really tough on us today", "SAFE"),
        ("I scored the winning goal!", "SAFE"),
        ("The referee made a terrible call", "SAFE"),
        ("We need to crush it at the tournament", "SAFE"),
        ("That runner is blazing fast", "SAFE"),
        ("The match was intense", "SAFE"),
        
        # Slang/Jokes (look dangerous but safe)
        ("That test was murder lol", "SAFE"),
        ("I'll kill you if you spoil the movie 😂", "SAFE"),
        ("I'm dying of laughter right now 🤣", "SAFE"),
        ("You're killing me with these jokes 😂", "SAFE"),
        ("I'm dead 💀💀💀", "SAFE"),
        ("This homework is killing me", "SAFE"),
        ("I'm going to die if I don't pass this test", "SAFE"),
        ("Bruh I'm literally dying 😂😂", "SAFE"),
        ("You slayed that presentation", "SAFE"),
        ("That joke killed me haha", "SAFE"),
        ("I'm so done with this class lol", "SAFE"),
        ("RIP my grade in history", "SAFE"),
        ("Yo that's fire 🔥", "SAFE"),
        ("This is bussin no cap", "SAFE"),
        ("Slay queen 💅", "SAFE"),
        
        # General casual
        ("What's for lunch today?", "SAFE"),
        ("I had pizza, it was so good", "SAFE"),
        ("Happy birthday! Hope you have a great day", "SAFE"),
        ("Thanks for the birthday wishes!", "SAFE"),
        ("Did you hear about the concert next week?", "SAFE"),
        ("I really want to go but tickets are expensive", "SAFE"),
        ("My mom said I can go to the party", "SAFE"),
        ("That's awesome! It's going to be so fun", "SAFE"),
        ("I got a new puppy yesterday!", "SAFE"),
        ("Aww that's so cute! What's its name?", "SAFE"),
        ("The weather is so nice today", "SAFE"),
        ("Want to go to the park after school?", "SAFE"),
        ("I just finished reading that book you recommended", "SAFE"),
        ("Did you like it?", "SAFE"),
        ("Yeah it was really good actually", "SAFE"),
        ("My parents are taking me to the beach", "SAFE"),
        ("I'm so jealous, have fun!", "SAFE"),
        ("What's your favorite ice cream flavor?", "SAFE"),
        ("Chocolate is the best obviously", "SAFE"),
        ("No way, vanilla is superior", "SAFE"),
        ("I can't believe summer is almost here", "SAFE"),
        ("I know right? This year went by so fast", "SAFE"),
        ("Who's your favorite teacher?", "SAFE"),
        ("Ms. Johnson is the best, she's so funny", "SAFE"),
        ("I agree, her class is always fun", "SAFE"),
        ("Want to trade Pokemon cards at lunch?", "SAFE"),
        ("Sure, I have some duplicates", "SAFE"),
        ("I learned a new song on guitar", "SAFE"),
        ("Can you play it for me sometime?", "SAFE"),
        ("I'll play it tomorrow at school", "SAFE"),
        ("My sister is so annoying sometimes", "SAFE"),
        ("Haha siblings can be like that", "SAFE"),
        ("I'm learning to cook pasta", "SAFE"),
        ("That's cool! Is it hard?", "SAFE"),
        ("Not really, my dad taught me", "SAFE"),
        ("BRB my mom is calling me for dinner", "SAFE"),
        ("Ok talk to you later!", "SAFE"),
        ("Good night! See you tomorrow", "SAFE"),
        ("Night! Sleep well", "SAFE"),
        ("I love your new profile picture", "SAFE"),
        ("Thanks I took it at the park", "SAFE"),
        ("Do you want to be partners for the project?", "SAFE"),
        ("Yes! We always work well together", "SAFE"),
        ("I'm nervous about the presentation", "SAFE"),
        ("Don't be, you're going to do great", "SAFE"),
        ("Thanks for always being supportive", "SAFE"),
        ("That's what friends are for", "SAFE"),
        ("I'm bored, nothing to do", "SAFE"),
        ("Same, let's video call and watch something", "SAFE"),
        ("I just got my test back, I got an A!", "SAFE"),
        ("That's amazing, congratulations!", "SAFE"),
        
        # ============================================================
        # BULLYING - 55 samples
        # ============================================================
        ("You're so ugly nobody wants to be your friend", "BULLYING"),
        ("Everyone in school hates you", "BULLYING"),
        ("You're worthless and stupid", "BULLYING"),
        ("Nobody likes you, just leave", "BULLYING"),
        ("You're the ugliest person I've ever seen", "BULLYING"),
        ("Why do you even come to school? Nobody wants you here", "BULLYING"),
        ("You're such a loser, everyone laughs at you behind your back", "BULLYING"),
        ("You smell so bad nobody wants to sit near you", "BULLYING"),
        ("You're so dumb you can't even pass the easiest test", "BULLYING"),
        ("Everyone thinks you're a joke", "BULLYING"),
        ("Why don't you just transfer schools? Nobody wants you here", "BULLYING"),
        ("You're pathetic and everyone knows it", "BULLYING"),
        ("I can't believe anyone would want to be friends with someone like you", "BULLYING"),
        ("You're so fat it's disgusting", "BULLYING"),
        ("You look like a freak", "BULLYING"),
        ("Nobody will ever love you because you're so ugly", "BULLYING"),
        ("You should be embarrassed to show your face", "BULLYING"),
        ("Everyone is talking about how weird you are", "BULLYING"),
        ("You're the most annoying person alive", "BULLYING"),
        ("Do everyone a favor and stop talking", "BULLYING"),
        ("You can't do anything right, you're useless", "BULLYING"),
        ("I'm going to tell everyone your secret", "BULLYING"),
        ("We don't want you in our group", "BULLYING"),
        ("You're not welcome here, leave", "BULLYING"),
        ("Stop trying to fit in, you never will", "BULLYING"),
        ("Your clothes are so ugly and cheap", "BULLYING"),
        ("You're such a crybaby, grow up", "BULLYING"),
        ("Nobody invited you, why are you even here?", "BULLYING"),
        ("You're an embarrassment to the whole class", "BULLYING"),
        ("I bet your parents are ashamed of you", "BULLYING"),
        ("You're a waste of space", "BULLYING"),
        ("Everyone would be happier if you weren't around", "BULLYING"),
        ("You're so stupid you make everyone else look smart", "BULLYING"),
        ("I screenshotted your photo and sent it to everyone", "BULLYING"),
        ("Haha look at this loser trying to be cool", "BULLYING"),
        ("You're never going to amount to anything", "BULLYING"),
        ("I dare you to show your face at the party", "BULLYING"),
        ("You're the reason nobody wants to hang out anymore", "BULLYING"),
        ("Just shut up already, nobody cares what you think", "BULLYING"),
        ("Your opinion doesn't matter because you're irrelevant", "BULLYING"),
        ("You're so poor you can't afford anything", "BULLYING"),
        ("Nice clothes, did you get them from the garbage?", "BULLYING"),
        ("You look ridiculous, everyone is laughing at you", "BULLYING"),
        ("Why are you so awkward? It's painful to watch", "BULLYING"),
        ("You're literally the worst person in this school", "BULLYING"),
        ("I told everyone not to sit with you at lunch", "BULLYING"),
        ("You're going to be alone forever", "BULLYING"),
        ("No one would even notice if you disappeared", "BULLYING"),
        ("You're nothing and you'll always be nothing", "BULLYING"),
        ("Eww don't touch me, you're gross", "BULLYING"),
        ("I feel sorry for anyone who has to be around you", "BULLYING"),
        ("You try so hard and you're still a failure", "BULLYING"),
        ("Even your friends talk behind your back about how lame you are", "BULLYING"),
        ("You're the kind of person people forget about", "BULLYING"),
        ("Everyone secretly can't stand you", "BULLYING"),
        
        # ============================================================
        # THREAT - 45 samples
        # ============================================================
        ("I will hurt you if you tell anyone", "THREAT"),
        ("I know where you live and I'm coming for you", "THREAT"),
        ("You're going to regret what you said to me", "THREAT"),
        ("I'll beat you up after school", "THREAT"),
        ("Wait until I find you, you'll be sorry", "THREAT"),
        ("I'm going to make your life a living hell", "THREAT"),
        ("If you tell the teacher I'll hurt you worse", "THREAT"),
        ("I'll find where you live and come to your house", "THREAT"),
        ("You better watch your back", "THREAT"),
        ("I'm going to beat you so bad you won't walk straight", "THREAT"),
        ("Tell anyone and I'll come after your family too", "THREAT"),
        ("I'll be waiting for you outside school", "THREAT"),
        ("You're dead when I see you tomorrow", "THREAT"),
        ("I will find you and make you pay", "THREAT"),
        ("Don't think you can hide from me", "THREAT"),
        ("I know your route home from school", "THREAT"),
        ("If you block me I'll find another way to get to you", "THREAT"),
        ("I'll make sure everyone turns against you", "THREAT"),
        ("You better sleep with one eye open", "THREAT"),
        ("I have your photos and I'll post them everywhere", "THREAT"),
        ("Mess with me again and see what happens", "THREAT"),
        ("I'm going to destroy your reputation", "THREAT"),
        ("I'll spread those screenshots if you don't do what I say", "THREAT"),
        ("You have no idea what I'm capable of", "THREAT"),
        ("I'll hack your account and ruin everything", "THREAT"),
        ("If you don't listen to me there will be consequences", "THREAT"),
        ("I know people who can make things very bad for you", "THREAT"),
        ("You're going to wish you never crossed me", "THREAT"),
        ("I will make you suffer for this", "THREAT"),
        ("I'll come to your school and find you", "THREAT"),
        ("Don't test me, you won't like what happens", "THREAT"),
        ("I'll ruin your life if you say anything", "THREAT"),
        ("You can't escape from me", "THREAT"),
        ("I'm going to get my friends and we'll come find you", "THREAT"),
        ("You better do what I say or else", "THREAT"),
        ("I'll hurt your little sister if you don't cooperate", "THREAT"),
        ("I know what school you go to", "THREAT"),
        ("I'm watching you and I know everything you do", "THREAT"),
        ("If you ignore me I'll show up at your door", "THREAT"),
        ("I will end you", "THREAT"),
        ("You think you're safe but you're not", "THREAT"),
        ("I'm coming for you and there's nothing you can do", "THREAT"),
        ("Keep talking and see what happens to you", "THREAT"),
        ("I'll make sure you never feel safe again", "THREAT"),
        ("This isn't over, I'll get my revenge", "THREAT"),
        
        # ============================================================
        # GROOMING - 45 samples
        # ============================================================
        ("Don't tell your parents about us talking", "GROOMING"),
        ("You're so mature for your age", "GROOMING"),
        ("Can you send me a private photo of yourself", "GROOMING"),
        ("This is our little secret okay?", "GROOMING"),
        ("You're not like other kids, you're special", "GROOMING"),
        ("I would never hurt you, I only want what's best for you", "GROOMING"),
        ("Your parents wouldn't understand our friendship", "GROOMING"),
        ("Can I see what you look like? Send a selfie", "GROOMING"),
        ("You're the only one who truly understands me", "GROOMING"),
        ("Let's keep our conversations just between us", "GROOMING"),
        ("I'll buy you whatever you want if you do something for me", "GROOMING"),
        ("You're so beautiful, has anyone ever told you that?", "GROOMING"),
        ("I feel a special connection with you", "GROOMING"),
        ("Your friends are jealous of how special you are", "GROOMING"),
        ("I've never met someone as mature as you", "GROOMING"),
        ("Can you turn on your camera so I can see you?", "GROOMING"),
        ("Don't let anyone see our messages", "GROOMING"),
        ("I got you a surprise gift, but keep it secret", "GROOMING"),
        ("You can trust me more than anyone else", "GROOMING"),
        ("I understand you better than your parents do", "GROOMING"),
        ("Would you like me to send you a gift? A new phone maybe?", "GROOMING"),
        ("You're so grown up for your age, not like other kids", "GROOMING"),
        ("Only I truly care about you", "GROOMING"),
        ("Your parents don't appreciate how special you are", "GROOMING"),
        ("Let me be the one who takes care of you", "GROOMING"),
        ("I want to see more of you, send me a video", "GROOMING"),
        ("Delete our chat history so no one sees it", "GROOMING"),
        ("You're different from everyone else, that's why I like talking to you", "GROOMING"),
        ("I have a secret I can only tell you", "GROOMING"),
        ("You make me feel so happy, no one else does", "GROOMING"),
        ("Can we talk on a different app where it's more private?", "GROOMING"),
        ("I'll send you money if you send me photos", "GROOMING"),
        ("Nobody needs to know about us", "GROOMING"),
        ("You're the most beautiful girl/boy I've ever seen", "GROOMING"),
        ("Let's meet up in person, but don't tell anyone", "GROOMING"),
        ("I'll take care of everything, just trust me", "GROOMING"),
        ("Do your parents check your phone? Let's be careful", "GROOMING"),
        ("I wish I could be with you right now", "GROOMING"),
        ("You're so pretty, do you know that?", "GROOMING"),
        ("I love talking to you, you're my favorite person", "GROOMING"),
        ("Don't show these messages to anyone okay?", "GROOMING"),
        ("I have something special planned for just the two of us", "GROOMING"),
        ("You don't need your other friends, I'm all you need", "GROOMING"),
        ("Promise me you'll keep this between us", "GROOMING"),
        ("I'll get you a new game if you do what I ask", "GROOMING"),
        
        # ============================================================
        # SELF_HARM - 35 samples
        # ============================================================
        ("I don't want to be alive anymore", "SELF_HARM"),
        ("Nobody would care if I disappeared", "SELF_HARM"),
        ("I wish I could just stop existing", "SELF_HARM"),
        ("Life isn't worth living anymore", "SELF_HARM"),
        ("I've been thinking about ending it all", "SELF_HARM"),
        ("Everyone would be better off without me", "SELF_HARM"),
        ("I hate myself and everything about my life", "SELF_HARM"),
        ("I don't see the point in going on", "SELF_HARM"),
        ("I've been hurting myself and I can't stop", "SELF_HARM"),
        ("I want the pain to stop permanently", "SELF_HARM"),
        ("Nobody would even notice if I was gone", "SELF_HARM"),
        ("I'm a burden to everyone around me", "SELF_HARM"),
        ("I don't want to wake up tomorrow", "SELF_HARM"),
        ("I've been cutting myself", "SELF_HARM"),
        ("Nothing matters anymore, I give up", "SELF_HARM"),
        ("I feel so empty inside, like nothing will ever get better", "SELF_HARM"),
        ("I just want to disappear forever", "SELF_HARM"),
        ("There's no point to any of this", "SELF_HARM"),
        ("I keep thinking about ways to end the pain", "SELF_HARM"),
        ("I'm so tired of pretending to be okay", "SELF_HARM"),
        ("I wish I was never born", "SELF_HARM"),
        ("The world would be better without me in it", "SELF_HARM"),
        ("I can't take it anymore, I want it to end", "SELF_HARM"),
        ("I've been having dark thoughts again", "SELF_HARM"),
        ("I started hurting myself again", "SELF_HARM"),
        ("Nobody cares if I live or die", "SELF_HARM"),
        ("I feel like there's no way out", "SELF_HARM"),
        ("I don't deserve to be happy", "SELF_HARM"),
        ("Everything is hopeless and pointless", "SELF_HARM"),
        ("I can't stop thinking about not being here anymore", "SELF_HARM"),
        ("I'm planning something and I won't be around much longer", "SELF_HARM"),
        ("I've written a note for my family", "SELF_HARM"),
        ("I want to go to sleep and never wake up", "SELF_HARM"),
        ("I punish myself because I deserve it", "SELF_HARM"),
        ("I'm looking at pills and wondering how many it would take", "SELF_HARM"),
        
        # ============================================================
        # PRIVACY_RISK - 45 samples
        # ============================================================
        ("What's your home address I want to visit", "PRIVACY_RISK"),
        ("Tell me your phone number", "PRIVACY_RISK"),
        ("What school do you go to and what class", "PRIVACY_RISK"),
        ("Where do you live exactly?", "PRIVACY_RISK"),
        ("What's your full name?", "PRIVACY_RISK"),
        ("Can you give me your address so I can mail you something", "PRIVACY_RISK"),
        ("What neighborhood do you live in?", "PRIVACY_RISK"),
        ("Send me your location", "PRIVACY_RISK"),
        ("What's your phone number so we can text instead", "PRIVACY_RISK"),
        ("Which school do you attend?", "PRIVACY_RISK"),
        ("What's your Instagram password? I'll fix your account", "PRIVACY_RISK"),
        ("Tell me your street address", "PRIVACY_RISK"),
        ("What area of town do you live in?", "PRIVACY_RISK"),
        ("Give me your Snapchat so we can talk privately", "PRIVACY_RISK"),
        ("What's your mom's phone number?", "PRIVACY_RISK"),
        ("What time do you usually get home from school?", "PRIVACY_RISK"),
        ("Do you walk home alone from school?", "PRIVACY_RISK"),
        ("Are your parents home right now?", "PRIVACY_RISK"),
        ("What's your last name?", "PRIVACY_RISK"),
        ("Can I get your cell number?", "PRIVACY_RISK"),
        ("What city do you live in?", "PRIVACY_RISK"),
        ("Tell me which bus you take", "PRIVACY_RISK"),
        ("What's your Wi-Fi password?", "PRIVACY_RISK"),
        ("Share your location with me", "PRIVACY_RISK"),
        ("What's your email and password?", "PRIVACY_RISK"),
        ("Where exactly is your house?", "PRIVACY_RISK"),
        ("Are you home alone right now?", "PRIVACY_RISK"),
        ("What time do your parents get home from work?", "PRIVACY_RISK"),
        ("Give me your address I'll come pick you up", "PRIVACY_RISK"),
        ("What grade and class are you in?", "PRIVACY_RISK"),
        ("Tell me what street you live on", "PRIVACY_RISK"),
        ("What's your home phone number?", "PRIVACY_RISK"),
        ("Which building do you live in?", "PRIVACY_RISK"),
        ("Where do your parents work?", "PRIVACY_RISK"),
        ("What's your apartment number?", "PRIVACY_RISK"),
        ("Do you have a landline number I can call?", "PRIVACY_RISK"),
        ("What route do you take to school?", "PRIVACY_RISK"),
        ("Where do you hang out after school?", "PRIVACY_RISK"),
        ("What time are you usually alone at home?", "PRIVACY_RISK"),
        ("Can you drop a pin of your location?", "PRIVACY_RISK"),
        ("What's the name of your school?", "PRIVACY_RISK"),
        ("Tell me your class schedule", "PRIVACY_RISK"),
        ("Where do you go after school before your parents get home?", "PRIVACY_RISK"),
        ("What's the nearest landmark to your house?", "PRIVACY_RISK"),
        ("Can you share your live location with me?", "PRIVACY_RISK"),
        
        # ============================================================
        # MANIPULATION - 35 samples
        # ============================================================
        ("If you really loved me you would do this", "MANIPULATION"),
        ("You owe me after everything I've done for you", "MANIPULATION"),
        ("Prove that you trust me by sending a photo", "MANIPULATION"),
        ("After all I've sacrificed for you this is how you treat me", "MANIPULATION"),
        ("If you don't do this I'll hurt myself and it's your fault", "MANIPULATION"),
        ("You're making me feel terrible by saying no", "MANIPULATION"),
        ("I thought we were friends but clearly you don't care", "MANIPULATION"),
        ("If you really cared about me you wouldn't say no", "MANIPULATION"),
        ("It will be your fault if something bad happens to me", "MANIPULATION"),
        ("You're the only person who can help me so you have to", "MANIPULATION"),
        ("I've done so much for you and you can't do this one thing?", "MANIPULATION"),
        ("If you leave me I'll have no one and it's your fault", "MANIPULATION"),
        ("You promised me you would do anything for me", "MANIPULATION"),
        ("Don't you want to prove you're a real friend?", "MANIPULATION"),
        ("I guess you never really cared about me at all", "MANIPULATION"),
        ("Everyone else would do it, why won't you?", "MANIPULATION"),
        ("If you tell anyone I'll tell everyone your secret", "MANIPULATION"),
        ("You need to do this for me because I said so", "MANIPULATION"),
        ("I'll stop being your friend if you don't help me", "MANIPULATION"),
        ("You owe me big time, don't forget that", "MANIPULATION"),
        ("Remember when I helped you? Now it's your turn", "MANIPULATION"),
        ("If you were a good person you would do this", "MANIPULATION"),
        ("You're being selfish by not doing what I ask", "MANIPULATION"),
        ("I'll tell everyone what you did unless you do this", "MANIPULATION"),
        ("You have no choice, you have to do what I say", "MANIPULATION"),
        ("I'll make your life miserable if you say no", "MANIPULATION"),
        ("You're making me so angry by not listening", "MANIPULATION"),
        ("Do it for me please I'm begging you, you owe me", "MANIPULATION"),
        ("If you refuse I'll know you never cared", "MANIPULATION"),
        ("This is what friends do for each other, just do it", "MANIPULATION"),
        ("I helped you so many times, you can't say no now", "MANIPULATION"),
        ("If you don't do this I'm going to do something drastic", "MANIPULATION"),
        ("Stop being difficult and just say yes", "MANIPULATION"),
        ("You're so ungrateful after everything I've done", "MANIPULATION"),
        ("I thought I could count on you but I guess not", "MANIPULATION"),
        
        # ============================================================
        # SCAM - 25 samples
        # ============================================================
        ("You won a free iPhone click this link", "SCAM"),
        ("Send me a gift card and I'll pay you back double", "SCAM"),
        ("Congratulations you've been selected for a free prize", "SCAM"),
        ("Click this link to claim your reward", "SCAM"),
        ("I need you to send me money urgently", "SCAM"),
        ("Buy a Steam gift card and send me the code", "SCAM"),
        ("You won the giveaway! Send me your details to claim", "SCAM"),
        ("I can double your money if you send me some first", "SCAM"),
        ("Go to this website and enter your login", "SCAM"),
        ("Send me an iTunes card and I'll Venmo you back", "SCAM"),
        ("I need a small loan, I'll pay you back tomorrow", "SCAM"),
        ("Click bit.ly/xyz to get free Robux", "SCAM"),
        ("You've been chosen for a special promotion", "SCAM"),
        ("Transfer money to this account and I'll send it back plus more", "SCAM"),
        ("Your account has been compromised, click here to verify", "SCAM"),
        ("I'm giving away free V-Bucks, just click this link", "SCAM"),
        ("Send me your PayPal info I'll send you money", "SCAM"),
        ("You can get free stuff just go to this website", "SCAM"),
        ("I need your help with a financial emergency, send cash", "SCAM"),
        ("Buy an Amazon gift card for me and I'll repay you", "SCAM"),
        ("Free Fortnite skins at this link tinyurl.com/xyz", "SCAM"),
        ("I know a trick to get unlimited money online", "SCAM"),
        ("Your phone has a virus, click here to fix it", "SCAM"),
        ("I'm a Nigerian prince and I need your help with money", "SCAM"),
        ("Send crypto to this wallet and I'll double it", "SCAM"),
        ("Send your credit card info to receive the reward", "SCAM"),
        ("Click this link to claim your $1000 gift voucher", "SCAM"),
        ("Invest $50 in this crypto scheme and get $500", "SCAM"),
        ("Send me your login credentials to unlock premium features", "SCAM"),

        # ============================================================
        # EXTENDED VOCABULARY: THREAT (Unseen violence actions, weapons, intimidation)
        # ============================================================
        ("I will strangle you until you stop breathing", "THREAT"),
        ("I'm going to choke you if you show up here", "THREAT"),
        ("I'll punch your teeth out next time I see you", "THREAT"),
        ("I am going to bash your face in", "THREAT"),
        ("I'll batter you senseless after class", "THREAT"),
        ("I'm going to stab you with a knife", "THREAT"),
        ("I have a blade and I'm not afraid to use it on you", "THREAT"),
        ("I'll slice you up if you open your mouth", "THREAT"),
        ("I am going to shoot you dead", "THREAT"),
        ("I have a gun in my bag and your name is on it", "THREAT"),
        ("I will hunt you down wherever you run", "THREAT"),
        ("I've been stalking you and I know your daily routine", "THREAT"),
        ("I'll jump you with my gang on your way home", "THREAT"),
        ("I'm going to break your legs so you can't walk", "THREAT"),
        ("I'll break your neck if you cross me again", "THREAT"),
        ("I will put you in the hospital", "THREAT"),
        ("You will end up in a coma when I'm finished with you", "THREAT"),
        ("I'll bury you six feet deep", "THREAT"),
        ("Count your days, you don't have much time left", "THREAT"),
        ("Say your prayers because you're dead meat", "THREAT"),
        ("I will slaughter you like an animal", "THREAT"),
        ("I will execute you where you stand", "THREAT"),
        ("I'm going to poison your drink", "THREAT"),
        ("I will burn your house down with you inside", "THREAT"),
        ("I'll drown you in the pool", "THREAT"),
        ("I'm going to assault you the moment you step outside", "THREAT"),
        ("I will slit your throat in your sleep", "THREAT"),
        ("I am going to track your location and attack you", "THREAT"),
        ("I will doxx you and post your private address online", "THREAT"),
        ("I'm going to swat your house and call armed police on you", "THREAT"),
        ("I will leak all your private photos to your classmates", "THREAT"),
        ("I'll ruin your family and destroy everything you care about", "THREAT"),
        ("You won't survive the week, mark my words", "THREAT"),
        ("I will make you bleed until you beg for mercy", "THREAT"),
        ("Consider this your final warning before I hurt you", "THREAT"),
        ("I'm going to kidnap you after school", "THREAT"),
        ("There is no escape for you, I'm right behind you", "THREAT"),

        # ============================================================
        # EXTENDED VOCABULARY: BULLYING (Vile insults, harassment, exclusion)
        # ============================================================
        ("You are a grotesque freak and everyone laughs at you", "BULLYING"),
        ("You look vile and completely repulsive", "BULLYING"),
        ("You are a worthless parasite that nobody cares about", "BULLYING"),
        ("You're a disgusting scumbag, do the world a favor and leave", "BULLYING"),
        ("You're a clown and the entire school makes fun of you", "BULLYING"),
        ("Go crawl into a hole and rot, nobody wants you here", "BULLYING"),
        ("You're an absolute embarrassment to your entire family", "BULLYING"),
        ("You are a hopeless failure at everything you try", "BULLYING"),
        ("You're a brainless imbecile who can't do anything right", "BULLYING"),
        ("You belong in a dumpster with the rest of the trash", "BULLYING"),
        ("You are a pathetic outcast with zero friends", "BULLYING"),
        ("Everyone in our group chat agrees you are completely obnoxious", "BULLYING"),
        ("Nobody will ever love someone as hideous as you", "BULLYING"),
        ("Go cry to your mommy you little baby", "BULLYING"),
        ("You're a waste of oxygen, stop talking", "BULLYING"),
        ("You're so desperate for attention it makes everyone sick", "BULLYING"),
        ("We kicked you out of the group because you're unbearable", "BULLYING"),
        ("Look at this loser trying so hard to be relevant", "BULLYING"),
        ("You have no life and no future", "BULLYING"),

        # ============================================================
        # EXTENDED VOCABULARY: GROOMING (Coercion, boundary-pushing, secrecy)
        # ============================================================
        ("Sneak out of your bedroom window tonight and meet me", "GROOMING"),
        ("Meet me behind the park where there are no streetlights", "GROOMING"),
        ("Lock your bedroom door so your parents can't walk in", "GROOMING"),
        ("Take off your clothes and turn on the webcam", "GROOMING"),
        ("Send me a spicy picture of your body", "GROOMING"),
        ("Show me what you look like without your shirt on", "GROOMING"),
        ("Send me an intimate photo, just between the two of us", "GROOMING"),
        ("You have such a hot body for someone your age", "GROOMING"),
        ("Let's play an adult game that only grown-ups play", "GROOMING"),
        ("You can tell me anything, our chat is 100% confidential", "GROOMING"),
        ("Delete this conversation right now before your dad checks", "GROOMING"),
        ("Clear your browsing history so nobody discovers us", "GROOMING"),
        ("Don't mention our special friendship to your mother", "GROOMING"),
        ("Your parents are too strict and old-fashioned, they don't get you", "GROOMING"),
        ("I'm the only person in this world who truly appreciates you", "GROOMING"),
        ("I bought you an expensive gift, now you have to do what I ask", "GROOMING"),
        ("Are you in bed right now? What are you wearing?", "GROOMING"),
        ("Switch to Telegram or Signal so the messages disappear automatically", "GROOMING"),

        # ============================================================
        # EXTENDED VOCABULARY: SELF_HARM (Direct expressions, despair)
        # ============================================================
        ("I'm going to slit my wrists tonight", "SELF_HARM"),
        ("I took a razor blade to my arm again", "SELF_HARM"),
        ("I have a bottle of pills and I'm going to swallow them all", "SELF_HARM"),
        ("I tied a rope in my closet and I'm ready to hang myself", "SELF_HARM"),
        ("I want to jump off the bridge and end the misery", "SELF_HARM"),
        ("I'm going to drink bleach to stop this agony", "SELF_HARM"),
        ("This is my suicide note, please forgive me everyone", "SELF_HARM"),
        ("I can't endure this excruciating emotional pain anymore", "SELF_HARM"),
        ("I want to bleed out and never wake up again", "SELF_HARM"),
        ("Tonight is my final night on this earth", "SELF_HARM"),
        ("Goodbye cruel world, nobody will miss me when I'm gone", "SELF_HARM"),
        ("I am going to crash my bike on purpose so I don't survive", "SELF_HARM"),

        # ============================================================
        # EXTENDED VOCABULARY: PRIVACY_RISK (Direct geolocation & personal data)
        # ============================================================
        ("Drop your live location pin on WhatsApp right now", "PRIVACY_RISK"),
        ("Send me your exact GPS coordinates", "PRIVACY_RISK"),
        ("What is your street name and house number?", "PRIVACY_RISK"),
        ("Which floor and apartment number is yours?", "PRIVACY_RISK"),
        ("What time does your house stay empty during weekdays?", "PRIVACY_RISK"),
        ("Are your parents away on vacation this weekend?", "PRIVACY_RISK"),
        ("Give me your mother's credit card number and CVV", "PRIVACY_RISK"),
        ("What is the OTP code you just received on your phone?", "PRIVACY_RISK"),
        ("Send me your social security number or Aadhaar number", "PRIVACY_RISK"),
        ("What is your parent's annual income and bank name?", "PRIVACY_RISK"),
        ("Which exact bus stop do you wait at every morning alone?", "PRIVACY_RISK"),

        # ============================================================
        # EXTENDED VOCABULARY: SAFE CONTEXTS (Gaming, pop culture, sports, humor)
        # ============================================================
        ("I got a 10 kill streak in Call of Duty with a sniper rifle", "SAFE"),
        ("The final boss in Elden Ring is going to destroy me", "SAFE"),
        ("He planted the bomb on site A in Counter-Strike", "SAFE"),
        ("We eliminated the entire enemy squad in Apex Legends", "SAFE"),
        ("I sniped him through the smoke in Valorant", "SAFE"),
        ("The combat moves in Mortal Kombat are so brutal and crazy", "SAFE"),
        ("In GTA the police chase was insane with all the shooting", "SAFE"),
        ("The villain in the Batman movie got executed at the end", "SAFE"),
        ("That horror movie had so much blood and stabbing scenes", "SAFE"),
        ("In the detective series the murderer strangled the victim", "SAFE"),
        ("The fight choreographer in John Wick is incredible", "SAFE"),
        ("Our football team slaughtered the opponents 6 to 0", "SAFE"),
        ("We battered their defense during the entire second half", "SAFE"),
        ("That cricket bowler is lethal, he smashed the stumps", "SAFE"),
        ("That comedy routine had me choking on my drink from laughter 😂", "SAFE"),
        ("I'm dying laughing at this ridiculous meme 💀🤣", "SAFE"),
        ("That roast was savage, you destroyed him dude haha", "SAFE"),
        ("She totally slayed that dance performance on stage", "SAFE"),
        ("That chemistry exam was absolute murder, everyone failed", "SAFE"),
        ("My legs are completely dead after running that marathon", "SAFE"),
        # ============================================================
        # NEGATION & CONTEXTUAL AMBIGUITY (Safe statements containing risky words)
        # ============================================================
        ("I would never hurt you or anyone else", "SAFE"),
        ("Please do not kill yourself, you have so much to live for", "SAFE"),
        ("I am definitely not going to hurt you", "SAFE"),
        ("I do not hate you at all, you are my best friend", "SAFE"),
        ("Stop saying you will die, everything will be okay", "SAFE"),
        ("I do not want to fight anyone after school", "SAFE"),
        ("I am not going to let anyone bully you", "SAFE"),
        ("I promise I will never betray your trust", "SAFE"),
        ("The teacher said bullying will not be tolerated in class", "SAFE"),
        ("In history class we learned about how ancient armies fought battles", "SAFE"),
        ("We were discussing the tragedy in English literature class", "SAFE"),
        ("I told him to stop threatening other students and he listened", "SAFE"),

        # ============================================================
        # SLANG, ABBREVIATIONS & MISSPELLINGS (Realistic chat risks)
        # ============================================================
        ("kys nobody likes u in this school", "BULLYING"),
        ("u r such a pathetic loserrrr", "BULLYING"),
        ("everyone thx u r a total joke", "BULLYING"),
        ("i will k!ll u after school today", "THREAT"),
        ("im gonna k1ll u rn watch ur back", "THREAT"),
        ("i will beat u up after class bro", "THREAT"),
        ("u r dead meat when i find u", "THREAT"),
        ("wanna sneak out w/ me 2night? dont tell ur mom", "GROOMING"),
        ("send spicy pic on snap rn or i block u", "GROOMING"),
        ("send a pic of ur body just between us", "GROOMING"),
        ("send ur live location pin rn", "PRIVACY_RISK"),
        ("tell me ur home address rn or else", "PRIVACY_RISK"),
        ("i wanna kms so badly everything hurts", "SELF_HARM"),
        ("i wanna dieeee rn i cant take this", "SELF_HARM"),
        ("if u dont do this im gonna hurt myself and its ur fault", "MANIPULATION"),
        ("u owe me big time, do what i say rn", "MANIPULATION"),

        # ============================================================
        # INDIRECT RISKY EXPRESSIONS (Nuanced & subtle intimidation / grooming)
        # ============================================================
        ("It would be a real shame if something unexpected happened to you on your walk home", "THREAT"),
        ("You might want to look over your shoulder every step you take today", "THREAT"),
        ("Certain people know how to make problems like you disappear quietly", "THREAT"),
        ("I know people who handle people like you without leaving a trace", "THREAT"),
        ("Bad things tend to happen to kids who talk too much", "THREAT"),
        ("You will definitely regret opening your mouth about this", "THREAT"),
        ("Let us keep our special connection between just the two of us, nobody else needs to know", "GROOMING"),
        ("You are so much more mature and grown up than those silly kids in your grade", "GROOMING"),
        ("I bought you a really nice surprise, but you have to come alone to get it", "GROOMING"),
        ("Your parents are too old-fashioned to understand how special our bond is", "GROOMING"),
        ("Let's switch to an encrypted app where nobody can monitor our private chats", "GROOMING"),
        ("If you truly valued our friendship you would never hesitate to do this for me", "MANIPULATION"),
        ("After everything I have done for your family, this is the gratitude you show me?", "MANIPULATION"),
    ]
    
    # Check for optional user-provided custom dataset
    custom_data = load_custom_samples()
    if custom_data:
        training_data.extend(custom_data)
        
    return training_data


def load_custom_samples(filepath: str = None) -> list:
    """
    Load external labelled samples from a JSON or CSV file if provided.
    
    Expected JSON format:
        [{"text": "Sample sentence", "label": "CATEGORY"}, ...]
    Expected CSV format:
        text,label
    """
    import os, json, csv
    
    if not filepath:
        default_custom = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'custom_data.json')
        if os.path.exists(default_custom):
            filepath = default_custom
        else:
            return []
            
    if not os.path.exists(filepath):
        return []
        
    loaded = []
    try:
        if filepath.endswith('.json'):
            with open(filepath, 'r', encoding='utf-8') as f:
                records = json.load(f)
                for r in records:
                    if 'text' in r and 'label' in r:
                        loaded.append((str(r['text']), str(r['label'])))
        elif filepath.endswith('.csv'):
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'text' in row and 'label' in row:
                        loaded.append((str(row['text']), str(row['label'])))
    except Exception as e:
        print(f"Notice: Could not load custom dataset from {filepath}: {e}")
        
    return loaded


def get_label_descriptions():
    """Return descriptions for each label."""
    return {
        'SAFE': 'Normal, safe conversation with no risk indicators',
        'BULLYING': 'Cyberbullying, sustained insults, exclusion, or harassment',
        'THREAT': 'Direct threats of harm, violence, or intimidation',
        'GROOMING': 'Predatory grooming patterns including secrecy, flattery, and exploitation',
        'SELF_HARM': 'Expressions of self-harm, suicidal ideation, or extreme hopelessness',
        'PRIVACY_RISK': 'Inappropriate requests for personal information',
        'MANIPULATION': 'Emotional manipulation, guilt-tripping, or coercive control',
        'SCAM': 'Financial scams, phishing, or fraudulent schemes',
    }


def get_dataset_stats():
    """Return statistics about the training dataset."""
    data = get_training_data()
    from collections import Counter
    label_counts = Counter(label for _, label in data)
    return {
        'total_samples': len(data),
        'label_counts': dict(label_counts),
        'num_labels': len(label_counts),
    }


if __name__ == '__main__':
    stats = get_dataset_stats()
    print("\n=== Child Safety ML Training Dataset Statistics ===")
    print(f"Total samples: {stats['total_samples']}")
    print(f"Number of categories: {stats['num_labels']}")
    print("\nSamples per category:")
    for label, count in sorted(stats['label_counts'].items(), key=lambda x: -x[1]):
        print(f"  {label}: {count}")
