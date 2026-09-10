import LearningWorkspace from '../../../../components/LearningWorkspace';
export default async function Course({params}:{params:Promise<{course_id:string}>}){const {course_id}=await params;return <main className="main" style={{marginLeft:0}}><LearningWorkspace courseId={course_id}/></main>}
