create unique index if not exists courses_title_unique_idx on public.courses(title);

do $$
declare
  item record;
  course_id uuid;
  phase_id uuid;
  skill_id uuid;
  plans text[][] := array[
    array['Python Foundations','Python','https://www.freecodecamp.org/learn/python-v9/','Build a command-line expense tracker with tests.','Beginner','20'],
    array['Web Foundations: HTML and CSS','HTML','https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content','Build an accessible responsive portfolio landing page.','Beginner','18'],
    array['JavaScript for Interfaces','JavaScript','https://www.freecodecamp.org/learn/javascript-v9/','Build a browser-based habit tracker with local state.','Beginner','24'],
    array['React Frontend Engineering','React','https://react.dev/learn','Build a data-driven dashboard with reusable components.','Intermediate','22'],
    array['Git and Collaborative Delivery','Git','https://git-scm.com/book/en/v2','Ship a feature through branches, review, merge, and release notes.','Beginner','10'],
    array['SQL and Relational Data','SQL','https://www.freecodecamp.org/learn/relational-databases/','Design a normalized database and write analytical queries.','Beginner','24'],
    array['FastAPI Backend Development','FastAPI','https://fastapi.tiangolo.com/tutorial/','Build a validated REST API with auth, tests, and OpenAPI docs.','Intermediate','26'],
    array['REST APIs and Integration','FastAPI','https://developer.mozilla.org/en-US/docs/Web/HTTP','Integrate an external API with retries, validation, and error states.','Intermediate','16'],
    array['Docker and Reproducible Delivery','Docker','https://docs.docker.com/get-started/','Containerize a FastAPI plus database service with health checks.','Intermediate','18'],
    array['Data Structures and Algorithms','DSA','https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures-v8/','Implement and benchmark a small algorithm library.','Intermediate','30'],
    array['Statistics for Product Decisions','Statistics','https://www.khanacademy.org/math/statistics-probability','Analyze an experiment and communicate uncertainty responsibly.','Beginner','20'],
    array['Practical Machine Learning','Python','https://developers.google.com/machine-learning/crash-course','Train and evaluate a small classifier with a reproducible notebook.','Intermediate','28'],
    array['Cloud Fundamentals','Cloud','https://aws.amazon.com/training/digital/','Deploy a small service with logs, secrets, and a cost-aware architecture note.','Beginner','16'],
    array['Testing Python Applications','FastAPI','https://docs.pytest.org/en/stable/getting-started.html','Create a test pyramid for an API including failure-path tests.','Intermediate','14'],
    array['System Design and Technical Interviews','DSA','https://www.freecodecamp.org/news/systems-design-for-interviews/','Design a scalable URL shortener and defend trade-offs in a mock review.','Advanced','20']
  ];
  i int;
  phase_titles text[] := array['Understand the foundations','Build the guided implementation','Ship evidence and reflect'];
begin
  for i in 1..array_length(plans,1) loop
    insert into public.skills(name,category,market_demand,demand_trend) values (plans[i][2],'Phase 4 catalog',60,'steady') on conflict(name) do nothing;
    select id into skill_id from public.skills where name=plans[i][2] limit 1;
    insert into public.courses(title,description,skill_id,difficulty,estimated_hours,is_demo)
      values(plans[i][1],'Seeded free-source implementation plan. Complete the build, document evidence, and connect the result to OMEN verification.',skill_id,plans[i][5],plans[i][6]::int,true)
      on conflict(title) do update set description=excluded.description,skill_id=excluded.skill_id,difficulty=excluded.difficulty,estimated_hours=excluded.estimated_hours;
    select id into course_id from public.courses where title=plans[i][1] limit 1;
    for item in select * from unnest(phase_titles) with ordinality as t(title,ord) loop
      insert into public.course_phases(course_id,title,description,phase_order) values(course_id,item.title,'Use the linked free source, take notes, and produce a small checkpoint.',item.ord) returning id into phase_id;
      insert into public.learning_resources(phase_id,title,url,resource_type,estimated_minutes) values(phase_id,plans[i][1]||' free source',plans[i][3],'official_free_source',greatest(30,plans[i][6]::int*60/3));
    end loop;
  end loop;
end $$;
