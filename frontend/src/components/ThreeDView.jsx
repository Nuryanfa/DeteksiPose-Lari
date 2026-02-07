import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Grid, Center } from '@react-three/drei';
import * as THREE from 'three';

const Stickman = ({ landmarks }) => {
    // MediaPipe Pose Connections
    const connections = [
        [11, 12], [11, 13], [13, 15], [12, 14], [14, 16], // Arms
        [11, 23], [12, 24], [23, 24], // Torso
        [23, 25], [24, 26], [25, 27], [26, 28], [27, 29], [28, 30], [29, 31], [30, 32] // Legs
    ];

    if (!landmarks || landmarks.length === 0) return null;

    return (
        <group>
            {/* Joints */}
            {landmarks.map((val, idx) => {
                // MediaPipe World Landmarks: x is right, y is up (but inverted in raw?), z is toward camera
                // We need to scale/flip to match typical 3D scene (y up)
                // MP: y is negative up? let's check. usually inverted.
                // Let's assume standard mapping: x -> x, y -> -y, z -> -z
                if (idx > 32) return null; // Only body points
                return (
                    <mesh key={idx} position={[-val.x, -val.y, -val.z]} scale={0.05}>
                         <sphereGeometry />
                         <meshStandardMaterial color={idx < 11 ? "hotpink" : "orange"} />
                    </mesh>
                );
            })}

            {/* Bones */}
            {connections.map(([start, end], idx) => {
                const s = landmarks[start];
                const e = landmarks[end];
                if (!s || !e) return null;
                
                const startPos = new THREE.Vector3(-s.x, -s.y, -s.z);
                const endPos = new THREE.Vector3(-e.x, -e.y, -e.z);
                const points = [startPos, endPos];
                
                // Draw Line
                 const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);

                return (
                    <line key={idx} geometry={lineGeometry}>
                        <lineBasicMaterial attach="material" color="white" linewidth={2} />
                    </line>
                );
            })}
        </group>
    );
};

const ThreeDView = ({ landmarks }) => {
    return (
        <div className="h-64 w-full bg-gray-900 rounded-2xl overflow-hidden border border-gray-700 relative">
             <div className="absolute top-2 left-2 z-10 bg-black/50 px-2 py-1 rounded text-xs text-white font-mono">
                3D Digital Twin
            </div>
            <Canvas camera={{ position: [0, 0, 3], fov: 60 }}>
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} />
                <OrbitControls enablePan={false} />
                <Grid infiniteGrid sectionSize={1} cellColor="#6f6f6f" sectionColor="#9d4b4b" fadeDistance={10} />
                <Center>
                    <Stickman landmarks={landmarks} />
                </Center>
            </Canvas>
        </div>
    );
};

export default ThreeDView;
