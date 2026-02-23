import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Camera, FileCheck, TrendingUp, Users, DollarSign } from 'lucide-react';
import { PremiumButton, GlassCard, StaggerContainer, StaggerItem } from './PremiumUI';

// Investor Landing Page
export const InvestorLanding = () => {
  const stats = [
    { icon: DollarSign, value: "$45B", label: "Market Size" },
    { icon: Users, value: "43M", label: "Renter Households" },
    { icon: TrendingUp, value: "68%", label: "Outsource Bookkeeping" },
    { icon: Shield, value: "91%", label: "Talent Shortage" }
  ];

  const features = [
    {
      title: "Forensic-Grade 3D Capture",
      description: "Millimeter-accurate digital twins with cryptographic proof of authenticity",
      icon: Camera
    },
    {
      title: "Blockchain Anchoring",
      description: "Immutable evidence chain on Polygon, court-admissible worldwide",
      icon: Shield
    },
    {
      title: "Instant Verification",
      description: "Public verification portal, zero-trust evidence validation",
      icon: FileCheck
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 lg:py-32">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/5 to-purple-600/5" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <StaggerContainer className="text-center">
            <StaggerItem>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-8"
              >
                <span className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" />
                Pre-Seed Round Open
              </motion.div>
            </StaggerItem>

            <StaggerItem>
              <h1 className="text-5xl lg:text-7xl font-bold text-gray-900 mb-6">
                The Future of
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                  Rental Security
                </span>
              </h1>
            </StaggerItem>

            <StaggerItem>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-10">
                DepoSafety eliminates the $45B security deposit dispute market 
                through forensic-grade 3D evidence and blockchain verification.
              </p>
            </StaggerItem>

            <StaggerItem className="flex justify-center gap-4">
              <PremiumButton size="lg">
                View Demo
              </PremiumButton>
              <PremiumButton variant="secondary" size="lg">
                Download Pitch Deck
              </PremiumButton>
            </StaggerItem>
          </StaggerContainer>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <StaggerContainer className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <StaggerItem key={index}>
                <GlassCard className="text-center">
                  <stat.icon className="w-8 h-8 text-blue-600 mx-auto mb-4" />
                  <motion.div
                    initial={{ scale: 0 }}
                    whileInView={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 200, delay: index * 0.1 }}
                    className="text-4xl font-bold text-gray-900 mb-2"
                  >
                    {stat.value}
                  </motion.div>
                  <div className="text-gray-600">{stat.label}</div>
                </GlassCard>
              </StaggerItem>
            ))}
          </StaggerContainer>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Why DepoSafety Wins
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Patent-pending technology combining 3D vision, cryptography, and blockchain
            </p>
          </div>

          <StaggerContainer className="grid lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <StaggerItem key={index}>
                <GlassCard hover className="h-full">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mb-6">
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-3">
                    {feature.title}
                  </h3>
                  
                  <p className="text-gray-600">
                    {feature.description}
                  </p>
                </GlassCard>
              </StaggerItem>
            ))}
          </StaggerContainer>
        </div>
      </section>

      {/* Business Model Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-6">
                Revenue Model
              </h2>
              
              <div className="space-y-6">
                {[
                  { title: "B2C - Tenant Protection", price: "$29", period: "per scan", desc: "Move-in/move-out documentation" },
                  { title: "B2B - Property Managers", price: "$199", period: "per month", desc: "Unlimited scans, white-label" },
                  { title: "Enterprise - Insurance", price: "Custom", period: "", desc: "API access, bulk pricing" }
                ].map((tier, index) => (
                  <GlassCard key={index} className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900">{tier.title}</h3>
                      <p className="text-sm text-gray-600">{tier.desc}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-600">{tier.price}</div>
                      <div className="text-sm text-gray-500">{tier.period}</div>
                    </div>
                  </GlassCard>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-3xl p-8 text-white">
              <h3 className="text-2xl font-bold mb-6">Investment Opportunity</h3>
              
              <div className="space-y-4">
                <div className="flex justify-between">
                  <span>Pre-Seed Round</span>
                  <span className="font-bold">$500K</span>
                </div>
                
                <div className="flex justify-between">
                  <span>Valuation Cap</span>
                  <span className="font-bold">$4M</span>
                </div>
                
                <div className="flex justify-between">
                  <span>Use of Funds</span>
                  <span className="font-bold">18 months runway</span>
                </div>
                
                <div className="h-px bg-white/20 my-4" />
                
                <div className="text-sm opacity-90">
                  <strong>Milestones:</strong>
                  <ul className="mt-2 space-y-1 list-disc list-inside">
                    <li>10K users in Year 1</li>
                    <li>$1M ARR by Month 18</li>
                    <li>Series A ready</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl lg:text-4xl font-bold text-white mb-6">
            Join the Future of Rental Security
          </h2>
          
          <p className="text-xl text-blue-100 mb-10">
            Be part of the $45B disruption. Invest in DepoSafety today.
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <PremiumButton variant="secondary" size="lg" className="bg-white text-blue-600 hover:bg-gray-100">
              Schedule Demo
            </PremiumButton>
            
            <PremiumButton size="lg" className="bg-blue-800 text-white hover:bg-blue-900">
              Download Pitch Deck
            </PremiumButton>
          </div>
        </div>
      </section>
    </div>
  );
};

export default InvestorLanding;
