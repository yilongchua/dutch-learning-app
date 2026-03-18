export class WavRecorder {
  private audioContext: AudioContext | null = null;
  private processor: ScriptProcessorNode | null = null;
  private input: MediaStreamAudioSourceNode | null = null;
  private stream: MediaStream | null = null;
  private recording = false;
  private leftChannel: Float32Array[] = [];
  private sampleRate = 0;

  async start(): Promise<void> {
    this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    this.sampleRate = this.audioContext.sampleRate;
    this.input = this.audioContext.createMediaStreamSource(this.stream);
    this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);
    this.leftChannel = [];

    this.processor.onaudioprocess = (e) => {
      if (!this.recording) return;
      const left = e.inputBuffer.getChannelData(0);
      this.leftChannel.push(new Float32Array(left));
    };

    this.input.connect(this.processor);
    this.processor.connect(this.audioContext.destination);
    this.recording = true;
  }

  stop(): Blob {
    this.recording = false;
    this.stream?.getTracks().forEach((t) => t.stop());
    this.input?.disconnect();
    this.processor?.disconnect();
    const flat = this.flattenBuffer(this.leftChannel);
    return this.encodeWAV(flat);
  }

  private flattenBuffer(buffers: Float32Array[]): Float32Array {
    const len = buffers.reduce((acc, b) => acc + b.length, 0);
    const result = new Float32Array(len);
    let offset = 0;
    for (const b of buffers) {
      result.set(b, offset);
      offset += b.length;
    }
    return result;
  }

  private encodeWAV(samples: Float32Array): Blob {
    const buf = new ArrayBuffer(44 + samples.length * 2);
    const view = new DataView(buf);
    this.writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + samples.length * 2, true);
    this.writeString(view, 8, 'WAVE');
    this.writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, this.sampleRate, true);
    view.setUint32(28, this.sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    this.writeString(view, 36, 'data');
    view.setUint32(40, samples.length * 2, true);
    this.floatTo16BitPCM(view, 44, samples);
    return new Blob([view], { type: 'audio/wav' });
  }

  private floatTo16BitPCM(output: DataView, offset: number, input: Float32Array): void {
    for (let i = 0; i < input.length; i++, offset += 2) {
      const s = Math.max(-1, Math.min(1, input[i]));
      output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
    }
  }

  private writeString(view: DataView, offset: number, str: string): void {
    for (let i = 0; i < str.length; i++) {
      view.setUint8(offset + i, str.charCodeAt(i));
    }
  }
}
