sql_gen:
	../../env/bin/bench sql-gen --site erpdev.talplatform.ai --prefix tal_ --output-file "../apps/mawhub/mawhub/sqltypes/tal_models.py"

sql_gen_tables:
	../../env/bin/bench sql-gen-tables --site erpdev.talplatform.ai --tables "tabParsed Document Section,tabParsed Document,tabJob Opening,tabJob Applicant,tabInterview,tabInterview Feedback,tabJob Pipeline" --output-file "../apps/mawhub/mawhub/sqltypes/table_models.py"

