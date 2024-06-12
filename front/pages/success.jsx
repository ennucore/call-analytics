// pages/success.js

import dynamic from 'next/dynamic';
import { Inter } from 'next/font/google'
import { CardTitle, CardDescription, CardHeader, CardContent, CardFooter, Card } from "@/components/ui/card"

// Dynamically import the Fireworks preset to avoid SSR issues
const Fireworks = dynamic(() => import('react-canvas-confetti/dist/presets/fireworks'), {
  ssr: false,
});

function Success() {
  return (
    <div className="success-page">
      <Card>
        <CardHeader>
          <CardTitle>Upload Successful!</CardTitle>
          <CardDescription>Your file has been successfully uploaded and the script executed.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center">
            <p>We are processing your upload. This might take a while, please be patient.</p>
          </div>
        </CardContent>
      </Card>
      {/* Fireworks preset to run confetti only once */}
      <Fireworks/>
    </div>
  );
}

export default Success;
