**Web scraping with Scrapy from [turbo.az](https://turbo.az/)**

This project was created as a home assignment for the [Technest Scholarship Program](https://technest.idda.az/) web development course.

To try it out, clone the repository and set up a Python virtual environment:

`python -m venv <venv_name>`

Then, install the required modules:

`pip install -r requirements.txt`

This project utilizes PostgreSQL as its database. If you prefer not to use a database, simply delete the line `turboaz.pipelines.SaveToPostgresPipeline` from the `settings.py` file. If you wish to use a different database, you will need to make some minor edits.

To start scraping, move to turboaz folder and run
`scrapy crawl turbospider`
It will create a data.json file in addition to writing to the database.

You can also provide optional parameters:
`scrapy crawl turbospider -O output.csv`

You can also change default output from `settings.py`.