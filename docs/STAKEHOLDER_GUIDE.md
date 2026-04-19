# Stakeholder Guide: Catholic Ride Share

## Executive Summary

Catholic Ride Share is a volunteer-driven platform connecting Catholics who need transportation to Mass, Confession, and other church activities with volunteer drivers who are willing to help. This document addresses key concerns regarding **risk management**, **liability**, **security**, and **operational safety** for stakeholders evaluating or supporting this initiative.

**Key Points:**
- **Mission-driven, not profit-driven**: Focused on serving the Catholic community
- **Safety-first approach**: Multi-layered verification, background checks, and monitoring
- **Legal framework**: Clear liability limitations, insurance requirements, and compliance
- **Privacy-by-design**: Minimal data collection, strong encryption, GDPR/CCPA compliance
- **Transparency**: Open-source development, community oversight, clear governance

### Open-Source Deployment Model

Catholic Ride Share is designed as an **open-source platform** that can be installed and operated by different communities.

- A parish, diocese, or Catholic organization can self-host its own instance.
- Each instance can define local governance, policies, and legal review appropriate to its jurisdiction.
- The public repository provides shared code, documentation, and a place to collaborate on improvements.
- Future managed hosting may be offered, but it is optional and not required to adopt the platform.

In this document, references to "the platform" or "we" should be interpreted as applying to the maintainers and/or the operator of a specific deployment, depending on context.

---

## 1. Risk Assessment & Mitigation

### 1.1 Identified Risks

We have identified and planned mitigation strategies for the following risk categories:

#### **Safety Risks**
- **Risk**: Unvetted drivers could pose safety threats to riders
- **Mitigation**: 
  - Multi-step driver verification process (see Section 3.1)
  - Background checks through certified providers (Checkr)
  - Safe Environment training requirement
  - Continuous monitoring and rating system
  - Admin review and approval of all drivers before first ride
  - Ability to suspend or ban problematic users

#### **Liability Risks**
- **Risk**: Platform could be held liable for incidents during rides
- **Mitigation**:
  - Clear Terms of Service establishing platform as facilitator only
  - Driver insurance verification requirements
  - Limitation of liability clauses
  - Mandatory arbitration provisions where legally permitted
  - Incident reporting and documentation system

#### **Data Security Risks**
- **Risk**: User data could be compromised
- **Mitigation**:
  - Industry-standard encryption (TLS 1.3, AES-256)
  - Minimal data collection approach
  - Regular security audits
  - Secure authentication (JWT with refresh tokens)
  - SOC 2 compliance pathway planned
  - Regular penetration testing

#### **Financial Risks**
- **Risk**: Payment fraud or donation disputes
- **Mitigation**:
  - Stripe integration with fraud detection
  - Transparent fee disclosure
  - No platform fees on donations
  - Clear donation vs. payment distinction
  - Chargeback protection policies

#### **Reputational Risks**
- **Risk**: Negative incidents could harm Catholic community reputation
- **Mitigation**:
  - Proactive incident response plan
  - Clear communication channels
  - Parish partnership model
  - Community oversight board (planned)
  - Transparent incident reporting to stakeholders

### 1.2 Risk Monitoring

- **Ongoing monitoring**: Weekly review of incident reports
- **KPIs tracked**: Safety incidents, user complaints, system security alerts
- **Escalation procedures**: Clear process for serious incidents involving parish leadership and legal counsel
- **Regular audits**: Quarterly internal reviews, annual external security audits

---

## 2. Liability Framework

### 2.1 Legal Structure

**Platform Role**: In any deployment, Catholic Ride Share operates as a **facilitator/technology platform** connecting volunteers, not as a transportation provider or employer.

**Deployment Responsibility**: The organization operating a given instance (for example, a parish or diocese) is responsible for adopting and enforcing local terms, verification requirements, incident procedures, and legal compliance for that deployment.

**Key Legal Distinctions**:
- Drivers are **independent volunteers**, not employees or contractors
- Platform provides technology only, not transportation services
- Similar legal framework to other peer-to-peer platforms
- Compliance with state and federal regulations for volunteer services

### 2.2 Liability Limitations

**Terms of Service Include**:
- **Disclaimer of warranties**: Platform provided "as-is"
- **Limitation of liability**: Capped at amount paid (typically $0 for free rides)
- **Indemnification**: Users agree to indemnify platform for their actions
- **Assumption of risk**: Users acknowledge inherent risks of ride-sharing
- **Dispute resolution**: Mandatory arbitration where legally permitted

**Insurance Requirements**:
- **Driver insurance**: All drivers must maintain personal auto insurance meeting state minimums
- **Platform insurance**: General liability and cyber liability coverage (planned)
- **Excess coverage**: Exploring supplemental insurance options for additional protection

### 2.3 Compliance Considerations

**Regulatory Compliance**:
- Not subject to commercial transportation regulations (volunteer service)
- Compliance with data protection laws (GDPR, CCPA, state laws)
- Adherence to accessibility requirements (ADA compliance planned)
- Tax compliance for donation processing (IRS regulations)

**State-by-State Analysis**:
- Legal review conducted for each state before launch
- Specific insurance requirements vary by state
- Partnership with legal counsel experienced in nonprofit/volunteer law

### 2.4 Incident Response Protocol

**In case of incidents**:
1. **Immediate response**: 24/7 incident hotline
2. **Documentation**: Comprehensive incident report system
3. **Investigation**: Third-party review for serious incidents
4. **Communication**: Transparent disclosure to affected parties and stakeholders
5. **Remediation**: Policy updates and system improvements based on lessons learned

---

## 3. Security Architecture

### 3.1 Driver Verification Process

**Multi-Layer Verification**:

**Phase 1: Initial Application**
- Email and phone verification
- Government-issued ID upload and verification
- Vehicle registration and insurance documentation
- Self-declaration of criminal history and driving record

**Phase 2: Background Checks**
- Criminal background check (state and federal)
- Sex offender registry check
- Driving record check (MVR)
- Integration with Checkr or similar certified provider
- Continuous monitoring for new offenses

**Phase 3: Training & Certification**
- Safe Environment training completion (Virtus, CMGP, or equivalent)
- Platform safety guidelines acknowledgment
- Community standards agreement
- First aid/CPR certification (encouraged but not required)

**Phase 4: Admin Review**
- Manual review by platform administrators
- Parish reference verification (optional but encouraged)
- Final approval required before activation

**Ongoing Monitoring**:
- Annual background check renewals
- Continuous monitoring for license suspensions or new offenses
- User rating system with automatic review triggers
- Random quality assurance checks

### 3.2 Data Security & Privacy

**Data Protection Measures**:

**Encryption**:
- **In transit**: TLS 1.3 for all communications
- **At rest**: AES-256 encryption for sensitive data (SSN, payment info)
- **Database**: PostgreSQL with encrypted fields for PII
- **Backups**: Encrypted backup storage with access controls

**Access Controls**:
- Role-based access control (RBAC)
- Multi-factor authentication (MFA) for admin accounts
- Principle of least privilege
- Regular access audits and reviews
- Session management with automatic timeouts

**Privacy by Design**:
- **Minimal data collection**: Only essential information collected
- **Data minimization**: Automatic deletion of unnecessary data
- **Purpose limitation**: Data used only for stated purposes
- **User control**: Users can view, export, and delete their data

**Compliance**:
- **GDPR compliant**: For European users
- **CCPA compliant**: For California users
- **HIPAA awareness**: No health information collected
- **COPPA compliant**: No users under 13

### 3.3 Application Security

**Secure Development Practices**:
- Input validation on all user inputs (Pydantic schemas)
- SQL injection protection via ORM (SQLAlchemy)
- Cross-site scripting (XSS) prevention
- Cross-site request forgery (CSRF) tokens
- Rate limiting to prevent abuse
- Regular dependency updates and vulnerability scanning

**Authentication & Authorization**:
- JWT tokens with short expiration (30 min access, 7 day refresh)
- Bcrypt password hashing (cost factor 12)
- Password complexity requirements
- Account lockout after failed attempts
- Optional two-factor authentication

**Monitoring & Incident Response**:
- Real-time security monitoring and alerting
- Intrusion detection system (planned)
- Regular penetration testing
- Bug bounty program (planned)
- Security incident response plan
- Annual security audits by third-party firms

### 3.4 Platform Integrity

**Anti-Fraud Measures**:
- Phone and email verification required
- Device fingerprinting to detect multiple accounts
- Behavioral analysis for suspicious activity
- Integration with Stripe Radar for payment fraud
- Machine learning models for anomaly detection

**Content Moderation**:
- AI-powered content filtering for inappropriate messages
- Human review for flagged content
- Zero-tolerance policy for harassment or abuse
- Clear reporting mechanisms for users
- Rapid response team for safety concerns

---

## 4. Safety Features

### 4.1 Rider Safety Features

**Before the Ride**:
- Driver profile with photo, ratings, and vehicle information
- View driver's verification status
- See number of completed rides
- Read reviews from other riders
- Option to share ride details with emergency contacts

**During the Ride**:
- Real-time ride tracking shared with emergency contacts
- In-app emergency button (contacts authorities and platform)
- Live location sharing
- In-app messaging (monitored for safety keywords)
- Ability to call driver without revealing phone number

**After the Ride**:
- Rate and review driver
- Report safety concerns
- Access to ride history and receipts
- 24/7 support line for issues

### 4.2 Driver Safety Features

**Protection for Drivers**:
- Rider verification (email and phone required)
- Rider ratings visible before accepting
- Ability to decline rides without penalty
- Report problematic riders
- Insurance verification encouraged
- Safety tips and training materials

**Control & Autonomy**:
- Drivers choose which rides to accept (no obligation)
- Set availability schedules
- Define service areas (no distance limits, but optional preferences)
- Pause or deactivate account anytime
- Cancel rides with valid reasons

### 4.3 Community Standards

**Code of Conduct**:
- Respectful behavior required
- No discrimination based on protected classes
- No inappropriate conversations or behavior
- Respect for property and personal space
- Compliance with traffic laws
- Alcohol/drug-free operation

**Enforcement**:
- Clear consequences for violations
- Three-tier warning system
- Temporary suspension for serious violations
- Permanent ban for egregious violations or repeated offenses
- Right to appeal decisions

---

## 5. Privacy Policy Overview

### 5.1 Data Collection

**Information We Collect**:
- Account information (name, email, phone, password hash)
- Profile information (photo, parish affiliation)
- Driver information (license, insurance, vehicle, background check results)
- Location data (only during active ride requests/rides)
- Ride history and transaction records
- Device and usage information (for security and improvement)

**Information We Don't Collect**:
- Mass attendance times or schedules
- Specific church service preferences
- Confession schedules
- Health information
- Social Security Numbers (background check provider collects temporarily)
- Payment card numbers (handled by Stripe)

### 5.2 Data Usage

**How We Use Data**:
- Facilitate ride matching and coordination
- Verify identities and conduct background checks
- Process donations and payments
- Communicate about rides and platform updates
- Improve platform safety and functionality
- Comply with legal obligations

**How We Don't Use Data**:
- Never sold to third parties
- No advertising or marketing to third parties
- No profiling or behavioral tracking for commercial purposes
- No sharing with data brokers

### 5.3 Data Sharing

**Limited Sharing**:
- **With other users**: Only information necessary for ride coordination (name, photo, location for active rides)
- **With service providers**: Background check companies, payment processors, cloud hosting (AWS), email service
- **With law enforcement**: Only when legally required via valid legal process
- **With parishes**: Optional parish verification only with user consent

### 5.4 Data Retention

**Retention Periods**:
- Active accounts: Data retained while account is active
- Inactive accounts: Deleted after 2 years of inactivity (unless legal hold)
- Ride history: 7 years for safety and legal purposes
- Background checks: Retained per state requirements
- User can request deletion anytime (subject to legal obligations)

### 5.5 User Rights

**Your Rights**:
- Access your personal data
- Correct inaccurate data
- Delete your account and data
- Export your data (data portability)
- Opt-out of marketing communications
- Restrict processing in certain circumstances
- Object to automated decision-making

---

## 6. Terms of Service Overview

### 6.1 User Agreement Highlights

**Key Terms**:
- Users must be 18+ years old
- Accurate information required
- One account per person
- Compliance with laws and community standards
- Platform is facilitator only, not transportation provider
- No employment or agency relationship created

### 6.2 Driver-Specific Terms

**Driver Obligations**:
- Maintain valid license and insurance
- Complete all verification requirements
- Provide safe, reliable transportation
- Comply with traffic laws
- Maintain vehicle safety standards
- Respect rider privacy and dignity

**Driver Rights**:
- Choose which rides to accept
- Set own availability
- Receive optional donations (minus payment processing fees)
- Access to support and resources
- Fair treatment and due process

### 6.3 Rider-Specific Terms

**Rider Obligations**:
- Provide accurate pickup/dropoff information
- Be ready at pickup time
- Treat drivers with respect
- Comply with vehicle rules
- Optional donations encouraged but not required

**Rider Rights**:
- Request rides to church activities
- Choose drivers based on preferences
- Rate and review drivers
- Report safety concerns
- Access ride history

### 6.4 Dispute Resolution

**Process**:
1. Contact support for resolution attempt
2. Escalation to management if needed
3. Mediation option available
4. Binding arbitration (where permitted)
5. Waiver of class action rights (where permitted)

---

## 7. Insurance & Legal Compliance

### 7.1 Insurance Requirements

**Driver Insurance**:
- **Required**: Personal auto insurance meeting state minimum requirements
- **Verification**: Insurance documentation uploaded and verified
- **Ongoing**: Continuous verification during driver tenure
- **Coverage**: Primary coverage responsibility remains with driver's personal policy

**Platform Insurance (Planned)**:
- **General Liability**: Coverage for platform operations
- **Cyber Liability**: Data breach and security incident coverage
- **Directors & Officers**: Protection for organizational leadership
- **Errors & Omissions**: Professional liability coverage
- **Excess Liability**: Additional umbrella coverage

**Supplemental Coverage Exploration**:
- Evaluating gap coverage for periods when driver is available/en route
- Similar to models used by other ride-share platforms
- Cost-benefit analysis for community benefit vs. operational costs

### 7.2 Regulatory Compliance

**Transportation Regulations**:
- **Status**: Volunteer service, not commercial transportation
- **TNC Regulations**: Not subject to most Transportation Network Company regulations
- **Local Permits**: Compliance with local volunteer driver requirements
- **Interstate**: No interstate commerce regulatory obligations

**Tax Compliance**:
- **Donations**: Properly processed through Stripe
- **Reporting**: 1099-K issued per IRS requirements when thresholds met
- **Driver Income**: Drivers responsible for own tax obligations on donations received
- **Tax-Exempt Status**: Exploring 501(c)(3) status for organizational operations

**Accessibility Compliance**:
- **ADA**: Commitment to accessible platform and services
- **WCAG 2.1 AA**: Web/app accessibility standards
- **Accommodation**: Process for special assistance requests
- **Training**: Disability awareness training for drivers (optional but encouraged)

### 7.3 State-Specific Considerations

**Variation Across States**:
- Insurance minimums vary by state (verified per state)
- Some states have specific volunteer driver protections
- Background check requirements may vary
- Data privacy laws differ (e.g., California CCPA)

**Launch Strategy**:
- Phased rollout starting with states with clear volunteer protections
- Legal review completed before entering each new state
- Partnership with local legal counsel
- Ongoing monitoring of regulatory changes

---

## 8. Business Model & Sustainability

### 8.1 Financial Model

**Revenue**:
- **Donations**: Optional rider donations after rides (100% to driver minus payment processing)
- **Grants**: Catholic organizations, foundations focused on community service
- **Sponsorships**: Local parishes or dioceses supporting operations
- **Future**: Premium features for organizations (e.g., parish accounts)

**Costs**:
- **Development**: Ongoing platform development and maintenance
- **Infrastructure**: Cloud hosting, databases, storage (AWS/GCP)
- **Operations**: Background checks, insurance, support team
- **Legal & Compliance**: Legal counsel, compliance monitoring
- **Safety & Security**: Security audits, monitoring tools

**Sustainability Plan**:
- Year 1: Grant-funded development and pilot launch
- Year 2-3: Grow donation volume and grant partnerships
- Year 4+: Sustainable through combination of donations, grants, and optional premium features
- Goal: Break-even operations within 3-4 years

### 8.2 Nonprofit Structure

**Legal Entity**:
- **Current**: Open-source project, exploring legal structures
- **Planned**: 501(c)(3) nonprofit organization
- **Governance**: Board of directors with Catholic community representation
- **Mission**: Serve the community, not profit maximization

**Transparency**:
- Annual financial reports published
- Open-source codebase (MIT License)
- Community involvement in governance
- Clear disclosure of platform fees and costs

---

## 9. Governance & Oversight

### 9.1 Organizational Structure

**Board of Directors (Planned)**:
- Catholic clergy representation
- Technology and cybersecurity experts
- Legal and compliance professionals
- Community advocates
- Parish representatives

**Advisory Board**:
- Parish leaders from various communities
- Driver and rider representatives
- Safety and risk management experts
- Insurance professionals

### 9.2 Community Involvement

**Stakeholder Engagement**:
- Regular town halls with user community
- Parish partnership programs
- Feedback mechanisms and surveys
- Open development roadmap
- Community feature voting

**Transparency Initiatives**:
- Public incident reports (anonymized)
- Safety metrics dashboard
- Regular stakeholder updates
- Open-source code and documentation

### 9.3 Ethical Guidelines

**Operating Principles**:
- **Mission-first**: Serve the Catholic community above all
- **Dignity of person**: Respect for all users
- **Stewardship**: Responsible use of resources
- **Transparency**: Open communication with stakeholders
- **Continuous improvement**: Learn from mistakes and evolve

---

## 10. Implementation Roadmap

### 10.1 Current Status (Phase 1: Foundation)

**Completed**:
- Core backend architecture (FastAPI, PostgreSQL, Redis)
- User authentication and email verification
- Basic profile management
- Security infrastructure foundation
- Initial documentation

**In Progress**:
- Driver verification workflow
- Background check integration
- Ride request and matching system

### 10.2 Phase 2: Safety & Verification (Q1-Q2 2025)

**Key Milestones**:
- Complete background check integration (Checkr)
- Implement driver verification workflow
- Safe Environment training integration
- Insurance verification system
- Admin review and approval process
- Pilot launch with 2-3 partner parishes

### 10.3 Phase 3: Core Ride Features (Q2-Q3 2025)

**Key Milestones**:
- Full ride request and matching system
- Real-time ride tracking
- In-app messaging
- Emergency features
- Rating and review system
- Donation processing via Stripe

### 10.4 Phase 4: Scale & Enhance (Q4 2025 - 2026)

**Key Milestones**:
- Mobile app launch (Flutter)
- Expanded geographic coverage
- Advanced safety features
- AI-powered matching improvements
- Community governance implementation
- 501(c)(3) status achievement

### 10.5 Success Metrics

**Safety Metrics**:
- Incident rate < 0.1% of rides
- Background check completion rate > 99%
- User safety rating average > 4.5/5
- Response time to safety reports < 15 minutes

**Growth Metrics**:
- Active drivers: 1,000+ by end of Year 1
- Rides completed: 10,000+ by end of Year 1
- Parish partnerships: 50+ by end of Year 1
- User satisfaction: > 4.3/5 overall rating

**Financial Metrics**:
- Cost per ride < $2 by Year 2
- Grant funding secured: $500K+ in Year 1
- Path to sustainability by Year 4

---

## 11. Frequently Asked Questions (FAQ)

### Legal & Liability

**Q: Who is liable if there's an accident during a ride?**
A: The driver's personal auto insurance is the primary coverage. The platform's Terms of Service clarify that we act as a facilitator only. We're exploring supplemental coverage options and require all drivers to maintain adequate insurance.

**Q: Are drivers employees or independent contractors?**
A: Neither. Drivers are volunteers using the platform to coordinate charitable transportation services. There is no employment or contractor relationship.

**Q: What happens if a driver or rider violates the terms of service?**
A: Violations are reviewed by our team. Consequences range from warnings to temporary suspension to permanent bans, depending on severity. Users have a right to appeal.

### Safety & Security

**Q: How do you prevent bad actors from becoming drivers?**
A: Multi-layer verification including background checks, driving record checks, sex offender registry checks, Safe Environment training, insurance verification, and admin approval. Continuous monitoring and user ratings provide ongoing oversight.

**Q: What if I feel unsafe during a ride?**
A: Use the in-app emergency button to immediately contact authorities and platform support. Your live location is shared with emergency services. You can also contact our 24/7 safety line.

**Q: How is my personal data protected?**
A: Industry-standard encryption (TLS 1.3, AES-256), minimal data collection, regular security audits, and compliance with GDPR/CCPA. We never sell data to third parties.

### Financial

**Q: How much does it cost to use the platform?**
A: The platform is free to use. Riders can optionally offer donations to drivers after rides. Drivers can use the service at no cost (subject to their own vehicle/insurance costs).

**Q: Where do donation payments go?**
A: 100% of donations go to the driver, minus payment processing fees (typically 2.9% + $0.30 for Stripe). The platform takes no cut.

**Q: Is this a for-profit company?**
A: No. The codebase is an open-source community project. Communities can self-host and govern their own instances, and they may choose legal structures (including nonprofit models) appropriate for their local operations.

### Operational

**Q: How do you ensure drivers are properly trained?**
A: All drivers must complete Safe Environment training (Virtus, CMGP, or equivalent) and acknowledge our safety guidelines. We provide additional resources and recommend (but don't require) first aid/CPR certification.

**Q: What if a driver can't complete a ride?**
A: Drivers should cancel with as much notice as possible. For emergencies, we have protocols to help find alternative transportation. Repeated unreliable behavior results in account review.

**Q: How far will drivers travel?**
A: There's no distance limit. Drivers see the distance before accepting and can choose based on their availability and willingness. Rural communities often require longer trips, and that's okay.

---

## 12. Conclusion & Next Steps

### 12.1 Summary

Catholic Ride Share is designed with **safety, security, and risk mitigation** as core priorities. Through comprehensive background checks, multi-layer verification, clear legal frameworks, robust data protection, and community oversight, we aim to provide a trustworthy platform that serves the Catholic community's transportation needs while minimizing risks for all stakeholders.

### 12.2 For Potential Supporters

If you're considering supporting Catholic Ride Share:

1. **Review this document** thoroughly and note any additional questions
2. **Evaluate deployment options** (self-host now, or managed hosting later if offered)
3. **Review and adapt policies** (terms, insurance, verification, incident response) for your jurisdiction
4. **Pilot locally** with your parish/diocese using a limited initial rollout
5. **Contribute improvements** back to the open-source project

### 12.3 For Parish Leaders

We invite parishes and dioceses to adopt and shape the platform:

1. **Set up your own instance** using the project documentation
2. **Run legal and policy review** with local counsel and diocesan leadership
3. **Pilot program** with limited scope to test local fit
4. **Iterate locally** by customizing workflows for your community
5. **Broader rollout** once your local operators are ready

### 12.4 Contact Information

**For Stakeholder Inquiries**:
- GitHub Issues: [Open an issue](https://github.com/schoedel-learn/catholic-ride-share/issues) for questions or discussions
- Documentation: View this repository's documentation folder
- Security Issues: Report via GitHub Security Advisories or open a confidential issue

**For Partnership Opportunities**:
- Use GitHub Issues to express interest in partnerships
- Direct contact information will be established as the project matures
- For immediate inquiries, please open a GitHub discussion or issue

---

## Document Information

**Version**: 1.1  
**Last Updated**: April 2026  
**Next Review**: Quarterly  
**Owner**: Project Maintainers (see GitHub repository contributors)

This document is maintained as part of our commitment to transparency and stakeholder communication. For the latest version, please visit our GitHub repository documentation folder.

---

*"For I was hungry and you gave me food, I was thirsty and you gave me drink, I was a stranger and you welcomed me." - Matthew 25:35*
