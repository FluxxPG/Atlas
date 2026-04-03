"use client";

import { Canvas } from "@react-three/fiber";
import { Float, MeshDistortMaterial, Sphere } from "@react-three/drei";

export function OrbScene() {
  return (
    <div className="absolute inset-0 opacity-80">
      <Canvas camera={{ position: [0, 0, 4] }}>
        <ambientLight intensity={1.4} />
        <directionalLight position={[4, 4, 2]} intensity={2} color="#82f7d5" />
        <Float speed={2.4} rotationIntensity={1.2} floatIntensity={1.4}>
          <Sphere args={[1.15, 128, 128]} position={[0.8, 0.1, 0]}>
            <MeshDistortMaterial
              color="#4fd1c5"
              emissive="#0f766e"
              emissiveIntensity={0.8}
              roughness={0.08}
              metalness={0.2}
              distort={0.35}
              speed={2.1}
            />
          </Sphere>
        </Float>
      </Canvas>
    </div>
  );
}

