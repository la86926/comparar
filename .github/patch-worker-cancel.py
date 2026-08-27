from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='''let activeDiffWorker=null;
function diffWordsAsync(txtA,txtB){
  const total=txtA.length+txtB.length;
  if(total<30000||typeof Worker==="undefined") return Promise.resolve(Diff.diffWords(txtA,txtB));

  if(activeDiffWorker){
    activeDiffWorker.terminate();
    activeDiffWorker=null;
  }

  return new Promise((resolve,reject)=>{
'''
new='''let activeDiffTask=null;
function cancelActiveDiff(){
  if(!activeDiffTask)return;
  const task=activeDiffTask;
  activeDiffTask=null;
  task.worker.terminate();
  task.reject(new DOMException("Comparación reemplazada","AbortError"));
}

function diffWordsAsync(txtA,txtB){
  const total=txtA.length+txtB.length;
  if(total<30000||typeof Worker==="undefined") return Promise.resolve(Diff.diffWords(txtA,txtB));

  cancelActiveDiff();

  return new Promise((resolve,reject)=>{
'''
if old not in s: raise RuntimeError('worker start anchor not found')
s=s.replace(old,new,1)
old2='''    const worker=new Worker(url);
    activeDiffWorker=worker;
    URL.revokeObjectURL(url);

    const finish=()=>{
      if(activeDiffWorker===worker) activeDiffWorker=null;
      worker.terminate();
    };
'''
new2='''    const worker=new Worker(url);
    activeDiffTask={worker,reject};
    URL.revokeObjectURL(url);

    const finish=()=>{
      if(activeDiffTask&&activeDiffTask.worker===worker) activeDiffTask=null;
      worker.terminate();
    };
'''
if old2 not in s: raise RuntimeError('worker task anchor not found')
s=s.replace(old2,new2,1)
old3='''  clearTimeout(compareTimer);compareRun++;
  if(activeDiffWorker){activeDiffWorker.terminate();activeDiffWorker=null}
'''
new3='''  clearTimeout(compareTimer);compareRun++;
  cancelActiveDiff();
'''
if old3 not in s: raise RuntimeError('reset worker anchor not found')
s=s.replace(old3,new3,1)
p.write_text(s,encoding='utf-8')
print('Improved cancellation of superseded large-text comparisons')
