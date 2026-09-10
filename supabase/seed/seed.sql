insert into public.skills(name,category,market_demand,demand_trend) values
('Python','Programming',92,'rising'),('SQL','Data',88,'rising'),('Git','Tools',82,'steady'),('Statistics','Data',76,'rising'),('Power BI','Analytics',68,'rising'),('FastAPI','Backend',64,'rising'),('Cloud','Infrastructure',62,'rising'),('Communication','Professional',72,'steady'),('DSA','Foundations',70,'steady'),('React','Frontend',67,'steady'),('Excel','Analytics',74,'steady'),('Data Storytelling','Analytics',55,'rising') on conflict(name) do nothing;

insert into public.roles(name,description,market_demand) values
('Data Analyst','Turn messy data into decisions with analysis, dashboards, and clear storytelling.','High'),
('Software Engineer','Build reliable product experiences across APIs, systems, and interfaces.','High'),
('AI/ML Engineer','Design learning systems and ship models that create measurable product value.','Growing') on conflict(name) do nothing;

insert into public.courses(title,description,skill_id,difficulty,estimated_hours) select 'SQL for Decision Makers','Learn query thinking, joins, aggregation, and analytical storytelling.',id,'Beginner',24 from public.skills where name='SQL' and not exists(select 1 from public.courses where title='SQL for Decision Makers');
insert into public.courses(title,description,skill_id,difficulty,estimated_hours) select 'Python for Analytics','Build a practical analysis workflow from raw data to insight.',id,'Intermediate',32 from public.skills where name='Python' and not exists(select 1 from public.courses where title='Python for Analytics');

insert into public.market_snapshots(source,is_fallback,metadata) values('OMEN development market snapshot',true,'{"note":"Development-only fallback; replace with normalized provider data in production."}');

-- Role Skills (Benchmark skill requirements per institutional career track)
insert into public.role_skills (role_id, skill_id, required_level, is_preferred)
select r.id, s.id, rs.required_level, rs.is_preferred
from (values
  ('Data Analyst', 'Python', 75, false),
  ('Data Analyst', 'SQL', 90, false),
  ('Data Analyst', 'Statistics', 80, false),
  ('Data Analyst', 'Power BI', 72, false),
  ('Data Analyst', 'Excel', 75, false),
  ('Data Analyst', 'Data Storytelling', 60, false),
  ('Software Engineer', 'Python', 65, false),
  ('Software Engineer', 'Git', 80, false),
  ('Software Engineer', 'DSA', 78, false),
  ('Software Engineer', 'React', 65, false),
  ('Software Engineer', 'FastAPI', 62, false),
  ('Software Engineer', 'SQL', 55, false),
  ('AI/ML Engineer', 'Python', 90, false),
  ('AI/ML Engineer', 'Statistics', 82, false),
  ('AI/ML Engineer', 'SQL', 62, false),
  ('AI/ML Engineer', 'Cloud', 68, false),
  ('AI/ML Engineer', 'DSA', 62, false)
) as rs(role_name, skill_name, required_level, is_preferred)
join public.roles r on r.name = rs.role_name
join public.skills s on s.name = rs.skill_name
on conflict (role_id, skill_id) do nothing;

-- Companies
insert into public.companies (name, website)
select c.name, c.website
from (values
  ('Northstar Labs', 'https://northstar.example.com'),
  ('Apex Systems', 'https://apex.example.com'),
  ('CloudScale Technologies', 'https://cloudscale.example.com'),
  ('Cognitive Dynamics', 'https://cognitivedynamics.example.com')
) as c(name, website)
where not exists (select 1 from public.companies where name = c.name);

-- Jobs (Opportunities with deterministic eligibility parameters)
insert into public.jobs (company_id, role_id, title, description, ctc, location, minimum_cgpa, allowed_branches, max_backlogs, deadline, external_application_url, is_demo)
select 
  c.id as company_id,
  r.id as role_id,
  j.title,
  j.description,
  j.ctc,
  j.location,
  j.minimum_cgpa,
  j.allowed_branches,
  j.max_backlogs,
  j.deadline::date,
  j.external_application_url,
  true
from (values
  ('Northstar Labs', 'Data Analyst', 'Data Analyst', 'Own dashboards and analysis that help product teams make faster decisions.', '₹12–16 LPA', 'Bengaluru · Hybrid', 7.0, array['CSE','IT','ECE'], 0, '2026-10-18', 'https://example.com/apply/northstar'),
  ('Apex Systems', 'Software Engineer', 'Software Engineer', 'Build reliable product experiences across APIs, systems, and interfaces.', '₹14–18 LPA', 'Hyderabad · On-site', 7.5, array['CSE','IT'], 0, '2026-11-01', 'https://example.com/apply/apex'),
  ('CloudScale Technologies', 'Software Engineer', 'Cloud & Platform Engineer', 'Deploy, scale, and maintain automated cloud infrastructure and pipelines.', '₹10–14 LPA', 'Pune · Remote', 6.5, array['CSE','IT','ECE','EEE'], 1, '2026-10-30', 'https://example.com/apply/cloudscale'),
  ('Cognitive Dynamics', 'AI/ML Engineer', 'AI/ML Engineer', 'Design learning systems and ship models that create measurable product value.', '₹16–22 LPA', 'Bengaluru · On-site', 8.0, array['CSE','IT'], 0, '2026-11-15', 'https://example.com/apply/cognitivedynamics')
) as j(company_name, role_name, title, description, ctc, location, minimum_cgpa, allowed_branches, max_backlogs, deadline, external_application_url)
join public.companies c on c.name = j.company_name
join public.roles r on r.name = j.role_name
where not exists (
  select 1 from public.jobs where company_id = c.id and title = j.title
);

-- Job Requirements (Skill requirements per opportunity)
insert into public.job_requirements (job_id, skill_id, required_level, is_preferred)
select j.id, s.id, req.required_level, req.is_preferred
from (values
  ('Northstar Labs', 'Data Analyst', 'SQL', 75, false),
  ('Northstar Labs', 'Data Analyst', 'Python', 70, false),
  ('Northstar Labs', 'Data Analyst', 'Power BI', 65, false),
  ('Northstar Labs', 'Data Analyst', 'Statistics', 60, true),
  ('Apex Systems', 'Software Engineer', 'Python', 75, false),
  ('Apex Systems', 'Software Engineer', 'Git', 70, false),
  ('Apex Systems', 'Software Engineer', 'DSA', 75, false),
  ('Apex Systems', 'Software Engineer', 'FastAPI', 65, false),
  ('Apex Systems', 'Software Engineer', 'React', 60, true),
  ('CloudScale Technologies', 'Cloud & Platform Engineer', 'Cloud', 70, false),
  ('CloudScale Technologies', 'Cloud & Platform Engineer', 'Git', 75, false),
  ('CloudScale Technologies', 'Cloud & Platform Engineer', 'Python', 60, false),
  ('CloudScale Technologies', 'Cloud & Platform Engineer', 'SQL', 55, true),
  ('Cognitive Dynamics', 'AI/ML Engineer', 'Python', 85, false),
  ('Cognitive Dynamics', 'AI/ML Engineer', 'Statistics', 80, false),
  ('Cognitive Dynamics', 'AI/ML Engineer', 'SQL', 65, false),
  ('Cognitive Dynamics', 'AI/ML Engineer', 'Cloud', 65, true)
) as req(company_name, job_title, skill_name, required_level, is_preferred)
join public.companies c on c.name = req.company_name
join public.jobs j on j.company_id = c.id and j.title = req.job_title
join public.skills s on s.name = req.skill_name
on conflict (job_id, skill_id) do nothing;
