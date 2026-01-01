const VolMeterWorket = `
  class VolMeter extends AudioWorkletProcessor {
    volume
    updateIntervalInMS
    nextUpdateFrame

    constructor() {
      super()
      this.volume = 0
      this.updateIntervalInMS = 25
      this.nextUpdateFrame = this.updateIntervalInMS
      this.port.onmessage = event => {
        if (event.data.updateIntervalInMS) {
          this.updateIntervalInMS = event.data.updateIntervalInMS
        }
      }
    }

    get intervalInFrames() {
      return (this.updateIntervalInMS / 1000) * sampleRate
    }

    process(inputs) {
      const input = inputs[0]

      if (input.length > 0) {
        const samples = input[0]
        let sum = 0
        let rms = 0

        // Calculate Sum of Squares
        // 計算平方和
        for (let i = 0; i < samples.length; ++i) {
          sum += samples[i] * samples[i]
        }

        // Calculate RMS (Root Mean Square)
        // 計算 RMS (均方根)
        rms = Math.sqrt(sum / samples.length)

        // Smooth the volume change
        // 平滑音量變化
        this.volume = Math.max(rms, this.volume * 0.7)

        this.nextUpdateFrame -= samples.length
        if (this.nextUpdateFrame < 0) {
          this.nextUpdateFrame += this.intervalInFrames
          this.port.postMessage({volume: this.volume})
        }
      }

      return true
    }
  }`;

export default VolMeterWorket;
