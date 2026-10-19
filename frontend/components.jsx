// Adapted from UI TripleD Native Tabs (Base UI) and Native Magnetic (shadcn).
// Copyright (c) 2026 uitripled. MIT: assets/vendor/UITRIPLED-LICENSE.md.
import React, {useId, useState, useRef} from 'react';
import {createRoot} from 'react-dom/client';
import {Tabs} from '@base-ui/react/tabs';
import {motion, MotionConfig, useMotionValue, useSpring, useTransform, useReducedMotion} from 'framer-motion';
function NativeTabs(){
 const id=useId(); const [active,setActive]=useState('charts');
 const items=[['charts','Overview'],['table','All results'],['log','Run log']];
 function select(value){setActive(value);for(const view of document.querySelectorAll('.view')) view.hidden=view.id!==value;if(value==='charts') requestAnimationFrame(()=>{for(const name of ['plot-pi','plot-e']){const el=document.getElementById(name);if(el.data) window.Plotly.Plots.resize(el);}});}
 return <MotionConfig reducedMotion="user"><Tabs.Root value={active} onValueChange={select}><Tabs.List className="triple-tabs" aria-label="Result views">{items.map(([value,label])=><Tabs.Tab key={value} value={value} className="triple-tab" aria-controls={value}>{active===value&&<motion.span className="tab-pill" layoutId={id} transition={{type:'spring',duration:.45,bounce:.15}}/>}<span>{label}</span></Tabs.Tab>)}</Tabs.List></Tabs.Root></MotionConfig>;
}
function NativeMagnetic({children}){
 const ref=useRef(null);const reduced=useReducedMotion();const x=useMotionValue(0),y=useMotionValue(0);const sx=useSpring(x,{stiffness:300,damping:30}),sy=useSpring(y,{stiffness:300,damping:30});const tx=useTransform(sx,v=>v*.15),ty=useTransform(sy,v=>v*.15);
 function move(e){if(reduced||e.pointerType==='touch')return;const r=ref.current.getBoundingClientRect();x.set(e.clientX-r.left-r.width/2);y.set(e.clientY-r.top-r.height/2);}
 return <motion.div ref={ref} className="creator" onPointerMove={move} onPointerLeave={()=>{x.set(0);y.set(0);}} style={{x:reduced?0:tx,y:reduced?0:ty}}>{children}</motion.div>;
}
createRoot(document.getElementById('triple-tabs')).render(<NativeTabs/>);
createRoot(document.getElementById('creator')).render(<NativeMagnetic><img className="creator-logo" src="/assets/vendor/dengex-logo.png" alt="DengeX" width="1536" height="434"/><span><small>CRAFTED BY</small><strong>Dogukan Ercan</strong></span></NativeMagnetic>);
