import AssessmentWorkspace from '../../../../../../components/AssessmentWorkspace';
export default async function Assessment({params}:{params:Promise<{assessment_id:string}>}){const {assessment_id}=await params;return <main className="main" style={{marginLeft:0}}><AssessmentWorkspace assessmentId={assessment_id}/></main>}
