import Hero from '@/components/sections/hero'
import Navigation from '@/components/sections/navigation'
import EvilTwinThreat from '@/components/sections/evil-twin-threat'
import DetectionTechnology from '@/components/sections/detection-technology'
import Manifesto from '@/components/sections/manifesto'
import HowItWorks from '@/components/sections/how-it-works'
import CTA from '@/components/sections/cta'
import Footer from '@/components/sections/footer'

export default function Home() {
  return (
    <main className="bg-background text-foreground overflow-hidden">
      <Navigation />
      <Hero />
      <Manifesto />
      <EvilTwinThreat />
      <DetectionTechnology />
      <HowItWorks />
      <CTA />
      <Footer />
    </main>
  )
}
