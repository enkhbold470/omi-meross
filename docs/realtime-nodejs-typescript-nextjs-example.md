import { NextRequest, NextResponse } from 'next/server';
import { writeFile, mkdir } from 'fs/promises';
import { createReadStream } from 'fs';
import { join } from 'path';
import openai from '@/lib/openai';
import { prisma } from '@/lib/prisma';

/**
 * OMI Real-Time Audio Webhook
 * 
 * POST /api/omi/realtime
 * 
 * Receives real-time audio chunks from OMI wearable device, saves them as WAV files
 * every 10 seconds, and transcribes them using OpenAI Whisper API (English only).
 * 
 * Request body: Raw binary audio data (octet-stream)
 * Query params: ?sample_rate=16000&uid=session_id
 * 
 * Response:
 * {
 *   "message": "Audio received",
 *   "session_id": "...",
 *   "transcript": "..." (if transcription completed)
 * }
 */

// Validate OpenAI API key on initialization
console.log("[INIT] Initializing Satomi Real-Time Audio Webhook with Whisper...");

try {
  if (!process.env.OPENAI_API_KEY) {
    console.error("[INIT ERROR] OPENAI_API_KEY environment variable is not set!");
    throw new Error("OPENAI_API_KEY is required");
  }
  
  console.log("[INIT] OPENAI_API_KEY found");
  console.log("[INIT SUCCESS] Real-Time Audio Webhook initialized successfully");
} catch (error) {
  console.error("[INIT CRITICAL ERROR] Failed to initialize:", error);
  throw error;
}

// Audio file configuration
const AUDIO_SAVE_DIR = join(process.cwd(), 'audio');
const NUM_CHANNELS = 1; // Mono audio
const SAMPLE_RATE = 16000; // 16kHz
const BITS_PER_SAMPLE = 16; // 16-bit PCM

// Ensure audio directory exists
mkdir(AUDIO_SAVE_DIR, { recursive: true }).then(() => {
  console.log("[CONFIG] Audio save directory ready:", AUDIO_SAVE_DIR);
}).catch((error) => {
  console.error("[CONFIG ERROR] Failed to create audio directory:", error);
});

// Session management for audio accumulation
interface AudioSession {
  sessionId: string;
  createdAt: number;
  lastActivity: number;
  audioBuffer: Buffer[]; // Accumulated audio chunks for saving as WAV
  lastSaveTime: number; // Last time we saved/transcribed
  transcripts: string[]; // Array of transcripts from each 10-second interval
  saveTimer: NodeJS.Timeout | null; // Timer for 10-second saves
}

const activeSessions = new Map<string, AudioSession>();

// Audio processing interval (10 seconds)
const PROCESS_INTERVAL = 10 * 1000; // 10 seconds

// Clean up inactive sessions (older than 5 minutes)
const SESSION_TIMEOUT = 5 * 60 * 1000; // 5 minutes

setInterval(() => {
  console.log("[CLEANUP] Checking for inactive sessions...");
  const now = Date.now();
  let cleanedCount = 0;
  
  for (const [sessionId, session] of activeSessions.entries()) {
    if (now - session.lastActivity > SESSION_TIMEOUT) {
      console.log(`[CLEANUP] Closing inactive session: ${sessionId}`);
      
      // Clear timer
      if (session.saveTimer) {
        clearInterval(session.saveTimer);
      }
      
      activeSessions.delete(sessionId);
      cleanedCount++;
    }
  }
  
  if (cleanedCount > 0) {
    console.log(`[CLEANUP] Cleaned up ${cleanedCount} inactive session(s)`);
  }
}, 60000); // Run cleanup every minute

/**
 * Creates a WAV header for PCM16 audio
 */
function createWAVHeader(dataLength: number): Buffer {
  const byteRate = SAMPLE_RATE * NUM_CHANNELS * BITS_PER_SAMPLE / 8;
  const blockAlign = NUM_CHANNELS * BITS_PER_SAMPLE / 8;
  const header = Buffer.alloc(44);

  // RIFF header
  header.write('RIFF', 0, 'ascii');
  header.writeUInt32LE(36 + dataLength, 4);
  header.write('WAVE', 8, 'ascii');

  // fmt chunk
  header.write('fmt ', 12, 'ascii');
  header.writeUInt32LE(16, 16); // fmt chunk size
  header.writeUInt16LE(1, 20); // audio format (1 = PCM)
  header.writeUInt16LE(NUM_CHANNELS, 22); // number of channels
  header.writeUInt32LE(SAMPLE_RATE, 24); // sample rate
  header.writeUInt32LE(byteRate, 28); // byte rate
  header.writeUInt16LE(blockAlign, 32); // block align
  header.writeUInt16LE(BITS_PER_SAMPLE, 34); // bits per sample

  // data chunk
  header.write('data', 36, 'ascii');
  header.writeUInt32LE(dataLength, 40); // data size

  return header;
}

/**
 * Saves accumulated audio buffers as a WAV file
 */
async function saveAudioAsWAV(session: AudioSession): Promise<string> {
  console.log(`[WAV] Saving audio as WAV file for session: ${session.sessionId}`);
  
  try {
    if (session.audioBuffer.length === 0) {
      console.warn(`[WAV] No audio data to save`);
      return '';
    }

    // Combine all audio chunks
    const totalLength = session.audioBuffer.reduce((sum, chunk) => sum + chunk.length, 0);
    const combinedAudio = Buffer.concat(session.audioBuffer, totalLength);
    
    console.log(`[WAV] Combined audio size: ${combinedAudio.length} bytes`);
    
    if (combinedAudio.length === 0) {
      console.warn(`[WAV] No audio data to save`);
      return '';
    }

    // Create WAV header
    const wavHeader = createWAVHeader(combinedAudio.length);
    
    // Combine header and audio data
    const wavFile = Buffer.concat([wavHeader, combinedAudio]);
    
    // Generate filename with timestamp
    const now = new Date();
    const filename = `${String(now.getDate()).padStart(2, '0')}_${String(now.getMonth() + 1).padStart(2, '0')}_${now.getFullYear()}_${String(now.getHours()).padStart(2, '0')}_${String(now.getMinutes()).padStart(2, '0')}_${String(now.getSeconds()).padStart(2, '0')}_${session.sessionId.slice(0, 8)}.wav`;
    const filepath = join(AUDIO_SAVE_DIR, filename);
    
    // Write file
    await writeFile(filepath, wavFile);
    
    console.log(`[WAV SUCCESS] Saved WAV file: ${filename}`);
    console.log(`[WAV SUCCESS] File path: ${filepath}`);
    console.log(`[WAV SUCCESS] File size: ${wavFile.length} bytes`);
    
    // Clear buffer after saving
    session.audioBuffer = [];
    
    return filepath;
  } catch (error) {
    console.error(`[WAV ERROR] Failed to save WAV file:`, error);
    
    if (error instanceof Error) {
      console.error(`[WAV ERROR] Error name:`, error.name);
      console.error(`[WAV ERROR] Error message:`, error.message);
      console.error(`[WAV ERROR] Error stack:`, error.stack);
    }
    
    throw error;
  }
}

/**
 * Transcribes audio file using OpenAI Whisper API (English only)
 */
async function transcribeAudio(filepath: string): Promise<string> {
  console.log(`[WHISPER] Starting transcription for: ${filepath}`);
  
  try {
    const fileStream = createReadStream(filepath);
    
    const transcription = await openai.audio.transcriptions.create({
      file: fileStream,
      model: 'whisper-1',
      language: 'en', // English only
      response_format: 'text',
    });

    const transcript = typeof transcription === 'string' ? transcription : '';
    console.log(`[WHISPER SUCCESS] Transcription: "${transcript}"`);
    
    return transcript;
  } catch (error) {
    console.error(`[WHISPER ERROR] Failed to transcribe audio:`, error);
    
    if (error instanceof Error) {
      console.error(`[WHISPER ERROR] Error name:`, error.name);
      console.error(`[WHISPER ERROR] Error message:`, error.message);
      console.error(`[WHISPER ERROR] Error stack:`, error.stack);
    }
    
    throw error;
  }
}

/**
 * Processes audio: saves as WAV and transcribes with Whisper
 */
async function processAudioChunk(session: AudioSession): Promise<void> {
  console.log(`[PROCESS] Processing audio chunk for session: ${session.sessionId}`);
  
  try {
    if (session.audioBuffer.length === 0) {
      console.log(`[PROCESS] No audio to process`);
      return;
    }

    // Save audio as WAV file
    const filepath = await saveAudioAsWAV(session);
    
    if (!filepath) {
      console.log(`[PROCESS] No file saved, skipping transcription`);
      return;
    }

    // Transcribe with Whisper
    const transcript = await transcribeAudio(filepath);
    
    // Store transcript in memory and database
    if (transcript && transcript.trim()) {
      session.transcripts.push(transcript);
      console.log(`[PROCESS SUCCESS] Transcript stored in memory. Total transcripts: ${session.transcripts.length}`);
      
      // Save to Prisma database
      try {
        await prisma.transcript.create({
          data: {
            sessionId: session.sessionId,
            transcript: transcript.trim(),
            audioFilepath: filepath,
          },
        });
        console.log(`[DB SUCCESS] Transcript saved to database`);
      } catch (dbError) {
        console.error(`[DB ERROR] Failed to save transcript to database:`, dbError);
        // Continue even if DB save fails
      }
    } else {
      console.log(`[PROCESS] Empty transcript, not storing`);
    }
    
    // Update last save time
    session.lastSaveTime = Date.now();
    
  } catch (error) {
    console.error(`[PROCESS ERROR] Failed to process audio chunk:`, error);
    
    if (error instanceof Error) {
      console.error(`[PROCESS ERROR] Error details:`, error.message);
    }
  }
}

/**
 * Gets or creates an audio session
 */
function getOrCreateSession(sessionId: string): AudioSession {
  let session = activeSessions.get(sessionId);
  
  if (!session) {
    console.log(`[SESSION] Creating new audio session: ${sessionId}`);
    session = {
      sessionId,
      createdAt: Date.now(),
      lastActivity: Date.now(),
      audioBuffer: [],
      lastSaveTime: Date.now(),
      transcripts: [],
      saveTimer: null,
    };
    
    // Set up 10-second interval timer
    session.saveTimer = setInterval(() => {
      console.log(`[TIMER] 10-second interval reached for session: ${sessionId}`);
      processAudioChunk(session!).catch((error) => {
        console.error(`[TIMER ERROR] Failed to process audio:`, error);
      });
    }, PROCESS_INTERVAL);
    
    activeSessions.set(sessionId, session);
    console.log(`[SESSION SUCCESS] Session created with 10-second timer`);
  }
  
  return session;
}

export async function POST(request: NextRequest) {
  console.log("\n[POST] ========================================");
  console.log("[POST] Received POST request to OMI Realtime Audio endpoint");
  console.log("[POST] Timestamp:", new Date().toISOString());
  console.log("[POST] ========================================\n");
  
  try {
    // OMI sends raw binary audio data, not JSON
    // Session info comes from URL parameters
    const searchParams = request.nextUrl.searchParams;
    const sessionId = searchParams.get('uid') || searchParams.get('session_id');
    const sampleRate = searchParams.get('sample_rate');
    
    console.log("[POST] URL search params:", Object.fromEntries(searchParams.entries()));
    console.log("[POST] Session ID from URL:", sessionId);
    console.log("[POST] Sample rate:", sampleRate);

    // Validate session ID
    if (!sessionId) {
      console.error("[POST ERROR] No session ID provided in URL parameters");
      
      return NextResponse.json({ 
        error: 'Session ID required',
        message: 'Please provide a valid uid or session_id in the URL parameters',
      }, { status: 400 });
    }

    // Read request body as ArrayBuffer (binary audio data)
    console.log("[POST] Reading request body as binary data...");
    const audioArrayBuffer = await request.arrayBuffer();
    const audioBuffer = Buffer.from(audioArrayBuffer);
    
    console.log("[POST] Audio buffer size:", audioBuffer.length, "bytes");

    // If no audio data, just acknowledge
    if (!audioBuffer || audioBuffer.length === 0) {
      console.log("[POST] No audio data in this chunk, acknowledging...");
      
      return NextResponse.json({ 
        message: 'Listening...',
        session_id: sessionId,
        session_active: true,
      });
    }

    // Get or create session
    const session = getOrCreateSession(sessionId);
    session.lastActivity = Date.now();

    // Accumulate audio for saving as WAV (will be processed every 10 seconds)
    session.audioBuffer.push(audioBuffer);
    console.log(`[POST] Accumulated audio chunk. Total chunks: ${session.audioBuffer.length}`);
    console.log(`[POST] Total audio buffer size: ${session.audioBuffer.reduce((sum, chunk) => sum + chunk.length, 0)} bytes`);

    // Get latest transcript if available
    const latestTranscript = session.transcripts.length > 0 
      ? session.transcripts[session.transcripts.length - 1]
      : null;

    console.log("[POST SUCCESS] Audio chunk accumulated successfully");
    console.log("[POST] ========================================\n");
    
    return NextResponse.json({
      message: 'Audio received and accumulating',
      session_id: sessionId,
      accumulated_chunks: session.audioBuffer.length,
      latest_transcript: latestTranscript || null,
      total_transcripts: session.transcripts.length,
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error("\n[POST ERROR] ========================================");
    console.error('[POST ERROR] Error in OMI Realtime Audio webhook');
    console.error("[POST ERROR] Timestamp:", new Date().toISOString());
    
    if (error instanceof Error) {
      console.error("[POST ERROR] Error type:", error.constructor.name);
      console.error("[POST ERROR] Error name:", error.name);
      console.error("[POST ERROR] Error message:", error.message);
      console.error("[POST ERROR] Error stack:", error.stack);
    } else {
      console.error("[POST ERROR] Unknown error type:", typeof error);
      console.error("[POST ERROR] Error value:", error);
    }
    
    console.error("[POST ERROR] ========================================\n");
    
    const errorResponse = {
      error: 'Failed to process request',
      message: '⛩️ The path to understanding is temporarily clouded. Please try again, and I shall guide you.',
      details: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    };
    
    console.error("[POST ERROR] Sending error response:", errorResponse);
    
    return NextResponse.json(errorResponse, { status: 500 });
  }
}

// GET endpoint for status and info
export async function GET() {
  console.log("\n[GET] ========================================");
  console.log("[GET] Received GET request to OMI Realtime Audio endpoint");
  console.log("[GET] Timestamp:", new Date().toISOString());
  console.log("[GET] Sending status and info...");
  
  try {
    const activeSessionCount = activeSessions.size;
    const activeSessionIds = Array.from(activeSessions.keys());
    
    // Get session summaries
    const sessionSummaries = Array.from(activeSessions.entries()).map(([id, session]) => ({
      session_id: id,
      chunks_accumulated: session.audioBuffer.length,
      total_transcripts: session.transcripts.length,
      last_activity: new Date(session.lastActivity).toISOString(),
    }));
    
    console.log(`[GET] Active sessions: ${activeSessionCount}`);
    console.log(`[GET] Session IDs:`, activeSessionIds);
    
    const statusInfo = {
      status: 'active',
      service: 'Satomi - Real-Time Audio Transcription',
      description: 'OMI real-time audio integration with Whisper API (English only)',
      version: '4.0.0',
      audio_support: true,
      transcription_enabled: true,
      transcription_service: 'OpenAI Whisper API',
      language: 'en',
      processing_interval: '10 seconds',
      active_sessions: activeSessionCount,
      session_ids: activeSessionIds,
      session_summaries: sessionSummaries,
      timestamp: new Date().toISOString(),
    };
    
    console.log("[GET SUCCESS] Status info:", JSON.stringify(statusInfo, null, 2));
    console.log("[GET] ========================================\n");
    
    return NextResponse.json(statusInfo);
  } catch (error) {
    console.error("[GET ERROR] Error in GET handler:", error);
    console.error("[GET ERROR] ========================================\n");
    
    if (error instanceof Error) {
      console.error("[GET ERROR] Error details:", error.message);
      console.error("[GET ERROR] Stack:", error.stack);
    }
    
    return NextResponse.json({
      status: 'error',
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
    }, { status: 500 });
  }
}

