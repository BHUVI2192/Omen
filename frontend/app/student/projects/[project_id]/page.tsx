import ProjectsWorkspace from '../../../../components/ProjectsWorkspace';
export default async function Project({params}:{params:Promise<{project_id:string}>}){const {project_id}=await params;return <main className="main" style={{marginLeft:0}}><ProjectsWorkspace projectId={project_id}/></main>}
