// BLACKGATE animated background: drifting signal nodes that link up and react to the cursor
(function(){
  const c=document.getElementById('bg-canvas'); if(!c) return;
  const ctx=c.getContext('2d');
  const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let W,H,dpr,nodes=[],mouse={x:-9999,y:-9999};
  const LINK=140, PINK='255,79,154', VIOLET='139,92,246';
  function resize(){
    dpr=Math.min(window.devicePixelRatio||1,2);
    W=c.width=innerWidth*dpr; H=c.height=innerHeight*dpr;
    const n=Math.min(110,Math.floor(innerWidth*innerHeight/14000));
    nodes=Array.from({length:n},()=>({
      x:Math.random()*W,y:Math.random()*H,
      vx:(Math.random()-.5)*.35*dpr,vy:(Math.random()-.5)*.35*dpr,
      r:(Math.random()*1.4+.8)*dpr,hot:Math.random()<.22
    }));
  }
  function frame(t){
    ctx.clearRect(0,0,W,H);
    const L=LINK*dpr;
    for(const p of nodes){
      if(!reduce){
        p.x+=p.vx;p.y+=p.vy;
        if(p.x<0||p.x>W)p.vx*=-1; if(p.y<0||p.y>H)p.vy*=-1;
      }
      const dx=p.x-mouse.x,dy=p.y-mouse.y,d=Math.hypot(dx,dy);
      if(d<160*dpr&&d>0&&!reduce){p.x+=dx/d*.6*dpr;p.y+=dy/d*.6*dpr;}
    }
    for(let i=0;i<nodes.length;i++){
      const a=nodes[i];
      for(let j=i+1;j<nodes.length;j++){
        const b=nodes[j],d=Math.hypot(a.x-b.x,a.y-b.y);
        if(d<L){
          ctx.strokeStyle='rgba('+(a.hot||b.hot?PINK:VIOLET)+','+(1-d/L)*.35+')';
          ctx.lineWidth=dpr*.8;ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
        }
      }
      const pulse=a.hot?.6+.4*Math.sin(t/500+i):.7;
      ctx.fillStyle='rgba('+(a.hot?PINK:VIOLET)+','+pulse+')';
      ctx.beginPath();ctx.arc(a.x,a.y,a.r*(a.hot?1.4:1),0,6.283);ctx.fill();
    }
    if(!reduce) requestAnimationFrame(frame);
  }
  addEventListener('resize',resize);
  addEventListener('mousemove',e=>{mouse.x=e.clientX*dpr;mouse.y=e.clientY*dpr;});
  addEventListener('mouseleave',()=>{mouse.x=mouse.y=-9999;});
  resize(); requestAnimationFrame(frame);
})();
