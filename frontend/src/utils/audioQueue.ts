import { fetchTtsArrayBuffer } from '../api'

export class AudioQueuePlayer {
  private audioContext: AudioContext | null = null
  private queue: string[] = []
  private isPlaying = false
  private isPaused = false
  private currentSource: AudioBufferSourceNode | null = null
  private audioBuffers: AudioBuffer[] = []
  private isProcessing = false
  private isFinishedEnqueueing = false
  private isStopped = false
  private onStateChange: (state: 'playing' | 'paused' | 'stopped') => void

  constructor(onStateChange: (state: 'playing' | 'paused' | 'stopped') => void) {
    this.onStateChange = onStateChange
  }

  private initContext() {
    if (!this.audioContext) {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    }
  }

  public enqueue(text: string) {
    if (this.isStopped) return
    const clean = text.trim()
    if (!clean) return
    
    // Quick frontend check: if the chunk only contains markdown symbols/spaces, ignore it
    const withoutSymbols = clean.replace(/[*`#_>\-\[\]\(\)!\|\n\s]/g, '')
    if (!withoutSymbols) return
    
    this.queue.push(clean)
    this.processQueue()
  }

  public finish() {
    this.isFinishedEnqueueing = true
    this.checkStop()
  }

  private checkStop() {
    if (this.isFinishedEnqueueing && this.queue.length === 0 && this.audioBuffers.length === 0 && !this.currentSource) {
      this.stop()
    }
  }

  private async processQueue() {
    if (this.isProcessing) return
    this.isProcessing = true

    while (this.queue.length > 0) {
      const text = this.queue.shift()!
      try {
        const arrayBuffer = await fetchTtsArrayBuffer(text)
        if (this.isStopped) return
        
        this.initContext()
        const audioBuffer = await this.audioContext!.decodeAudioData(arrayBuffer)
        if (this.isStopped) return
        
        this.audioBuffers.push(audioBuffer)

        if (!this.isPlaying && !this.isPaused) {
          this.playNext()
        }
      } catch (err: any) {
        if (err.message && err.message.includes('清洗后文本为空')) {
          console.debug('TTS skipped an empty markdown chunk.')
        } else {
          console.warn('TTS Fetch/Decode skipped:', err.message || err)
        }
      }
    }

    this.isProcessing = false
    this.checkStop()
  }

  private playNext() {
    if (this.isStopped || this.audioBuffers.length === 0) {
      this.isPlaying = false
      this.checkStop()
      return
    }

    this.initContext()
    const buffer = this.audioBuffers.shift()!
    const source = this.audioContext!.createBufferSource()
    source.buffer = buffer
    source.connect(this.audioContext!.destination)

    source.onended = () => {
      this.currentSource = null
      this.playNext()
    }

    this.currentSource = source
    this.isPlaying = true
    this.isPaused = false
    this.onStateChange('playing')
    source.start(0)
  }

  public pause() {
    if (this.audioContext && this.audioContext.state === 'running') {
      this.audioContext.suspend()
      this.isPaused = true
      this.isPlaying = false
      this.onStateChange('paused')
    }
  }

  public resume() {
    if (this.audioContext && this.audioContext.state === 'suspended') {
      this.audioContext.resume()
      this.isPaused = false
      this.isPlaying = true
      this.onStateChange('playing')
    }
  }

  public stop() {
    this.isStopped = true
    this.queue = []
    this.audioBuffers = []
    this.isFinishedEnqueueing = true
    if (this.currentSource) {
      this.currentSource.onended = null
      this.currentSource.stop()
      this.currentSource = null
    }
    this.isPlaying = false
    this.isPaused = false
    if (this.audioContext && this.audioContext.state === 'suspended') {
      this.audioContext.resume()
    }
    this.onStateChange('stopped')
  }
}
