'use client';
/* @jsxImportSource react */

// ./components/component.tsx

/* use client */
import { CardTitle, CardDescription, CardHeader, CardContent, CardFooter, Card } from "@/components/ui/card"
import { useRouter } from 'next/navigation';  // Correct import for useRouter
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from 'react';
import { mirage  } from 'ldrs';
import dynamic from 'next/dynamic';
import ShineBorder from "@/components/magicui/shine-border";

mirage.register();


export function Component() {
  const [callId, setCallId] = useState('');
  const [agentName, setAgentName] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const Fireworks = dynamic(() => import('react-canvas-confetti/dist/presets/fireworks'), {
    ssr: false,
  });

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setUploadSuccess(false); // Reset upload success state on new submission

    const formData = new FormData();
    formData.append('callId', callId);
    formData.append('agentName', agentName);
    formData.append('file', file);

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      setLoading(false);
      if (response.ok) {
        setUploadSuccess(true);
      } else {
        console.error('Failed to upload:', result.error);
      }
    } catch (error) {
      console.error('Network or other error:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    if (uploadSuccess) {
      const timer = setTimeout(() => setUploadSuccess(false), 5000); // Optionally reset the success message after 5 seconds
      return () => clearTimeout(timer);
    }
  }, [uploadSuccess]);

  return (
    <form onSubmit={handleSubmit}  className="w-5/6 md:w-9/10 mx-auto my-10">
      {loading ? (
        <div className="text-center">
          <Card className="min-h-[50vh] flex items-center justify-center">
            <CardContent className="space-y-4">
              <l-mirage size="120" speed="2.5" color="white"></l-mirage>
              <p>We have received your request and are now processing it...</p>
            </CardContent>
          </Card>
        </div>
      ) : uploadSuccess ? (
        <Card className="min-h-[50vh] flex items-center justify-center">
          <CardContent className="text-center space-y-4">
            <Fireworks />
            <p>Upload successful! Your file has been processed.</p>
          </CardContent>
        </Card>
      ) : (
        <Card className="min-h-[50vh] flex items-center justify-center">
          <CardHeader>
            <CardTitle>Upload Call Recording</CardTitle>
            <CardDescription>Provide the details of the call and upload the recording.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="callId">Call ID</Label>
                <Input id="callId" placeholder="Enter call ID" value={callId} onChange={(e) => setCallId(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="agentName">Agent Name</Label>
                <Input id="agentName" placeholder="Enter agent name" value={agentName} onChange={(e) => setAgentName(e.target.value)} />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="recording">Call Recording</Label>
              <Input accept="audio/mp3" id="recording" type="file" onChange={(e) => setFile(e.target.files[0])} />
            </div>
          </CardContent>
          <CardFooter className="justify-end">
            <Button type="submit">Upload</Button>
          </CardFooter>
        </Card>
      )}
    </form>

  );
}

