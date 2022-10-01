HTML_PATH = "./content.html"
URL = "https://www.google.com/search?q=top+10+electricians+in+area&near=california"
DRIVER_PATH = "./chromedriver.exe"

organic = {
    "url": URL,
    "data": (
        (
            "The Best 10 Electricians in Chicago, Illinois - Yelp",
            "https://www.yelp.com/search?cflt=electricians&amp;find_loc=Chicago%2C+IL",
        ),
        (
            "Top 10 Electricians in USA - Virtuous Reviews",
            "https://www.virtuousreviews.com/top/on-demand-services/electricians",
        ),
    ),
}

local = {
    "url": URL,
    # "see_more_url": "https://www.google.com/search?near=california&tbs=lf:1,lf_ui:14&tbm=lcl&q=top+10+electricians+in+area&rflfq=1&num=10&sa=X&ved=2ahUKEwjUj-Svn7z6AhWMet4KHareCaoQjGp6BAgQEAE",
    "data": (
        (
            "Household Electric Inc.",
            # "https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwioqpLsvrz6AhV8m1YBHShHD7UQgU96BAgJEAw&url=https%3A%2F%2Fhouseholdelectricca.com%2F&usg=AOvVaw2BVH61UoMhYCwiOkPTSckY"
            "https://householdelectricca.com/",
        ),
        (
            "911 Plumbing & Electric INC",
            # "https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwioqpLsvrz6AhV8m1YBHShHD7UQgU96BAgLEA0&url=https%3A%2F%2F911plumbingelectric.com%2F&usg=AOvVaw2L8ZKm6FTSO6SmF7nYrxey",
            "https://911plumbingelectric.com/",
        ),
    ),
}

ads = {
    "url": URL,
    "data": (
        (
            "5,0",
            "(52)",
            "Closed",
            "10+ years in business · +1 559-240-4499",
        ),
        (
            "5,0",
            "(279)",
            "Open 24 hours",
            "20+ years in business · Fresno, CA, United States · +1 559-960-1922",
        ),
        ("4,6", "(34)", "Open 24 hours", "5+ years in business · +1 559-318-5900"),
    ),
}

related = {
    "url": URL,
    "data": (
        (
            "What do most Electricians charge per hour?",
            # "How Much Does It Cost To Hire An Electrician? - Forbes",
            # "between $50 and $100 per hour",
            # "According to HomeAdvisor, the average electrician hourly rate is",
            # "https://www.forbes.com/home-improvement/electrical/cost-to-hire-electrician/",
        ),
        (
            "Who is the most successful electrician?",
            # "10 Famous People You Never Knew Worked As Electricians",
            # "Benjamin Franklin",
            # "Known by many as the First American, a founding father and present on the $100 bill Benjamin Franklin was also possibly one of the first electricians in history. He was an inventor and experimenter who really helped the world understand what electricity was and how it worked.",
            # "https://www.tradeskills4u.co.uk/posts/famous-electricians",
        ),
    ),
}
