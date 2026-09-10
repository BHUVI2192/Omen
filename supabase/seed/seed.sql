insert into public.skills(name,category,market_demand,demand_trend) values
('Python','Programming',92,'rising'),('SQL','Data',88,'rising'),('Git','Tools',82,'steady'),('Statistics','Data',76,'rising'),('Power BI','Analytics',68,'rising'),('FastAPI','Backend',64,'rising'),('Cloud','Infrastructure',62,'rising'),('Communication','Professional',72,'steady'),('DSA','Foundations',70,'steady'),('React','Frontend',67,'steady'),('Excel','Analytics',74,'steady'),('Data Storytelling','Analytics',55,'rising') on conflict(name) do nothing;
insert into public.roles(name,description,market_demand) values
('Data Analyst','Turn messy data into decisions with analysis, dashboards, and clear storytelling.','High'),
('Software Engineer','Build reliable product experiences across APIs, systems, and interfaces.','High'),
('AI/ML Engineer','Design learning systems and ship models that create measurable product value.','Growing') on conflict(name) do nothing;
insert into public.courses(title,description,skill_id,difficulty,estimated_hours) select 'SQL for Decision Makers','Learn query thinking, joins, aggregation, and analytical storytelling.',id,'Beginner',24 from public.skills where name='SQL' and not exists(select 1 from public.courses where title='SQL for Decision Makers');
insert into public.courses(title,description,skill_id,difficulty,estimated_hours) select 'Python for Analytics','Build a practical analysis workflow from raw data to insight.',id,'Intermediate',32 from public.skills where name='Python' and not exists(select 1 from public.courses where title='Python for Analytics');
insert into public.market_snapshots(source,is_fallback,metadata) values('OMEN development market snapshot',true,'{"note":"Development-only fallback; replace with normalized provider data in production."}');
