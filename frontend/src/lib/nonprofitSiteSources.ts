export type NonprofitSiteSource = {
  slug: string;
  name: string;
  tagline: string;
  summary: string;
  mission: string;
  heroLabel: string;
  audience: string[];
  pillars: Array<{
    title: string;
    description: string;
  }>;
  values: Array<{
    title: string;
    description: string;
  }>;
  featuredLinks: Array<{
    label: string;
    href: string;
  }>;
  founder: {
    name: string;
    role: string;
    bio: string;
    profileHref: string;
  };
  highlights: string[];
  callsToAction: Array<{
    label: string;
    href: string;
  }>;
};

export const catholicWorkSource: NonprofitSiteSource = {
  slug: "catholic-work",
  name: "Catholic.Work",
  tagline: "Building new roads to Emmaus in the digital city.",
  summary:
    "Catholic.Work is a digital apostolate that helps families, parishes, and dioceses form missionary disciples through practical formation, faithful encouragement, and technology that serves the Church.",
  mission:
    "Catholic.Work exists to build up the Church by helping Catholics repent, believe, and seek the Kingdom as missionary disciples in daily life. Its messaging centers on faith, hope, and love while creating practical pathways for formation, evangelization, and communion in a digital world.",
  heroLabel: "Catholic digital apostolate",
  audience: [
    "Families who want to live more intentionally as domestic churches",
    "Parishes that want to evangelize, accompany, and form new disciples",
    "Dioceses and ministries looking for faithful digital pathways for formation",
  ],
  pillars: [
    {
      title: "Domestic churches",
      description:
        "Encourage parents and families to hand on the faith at home with practical support, hope-filled encouragement, and a clear missionary identity.",
    },
    {
      title: "Christian initiation",
      description:
        "Help parishes proclaim the Gospel, welcome seekers, and accompany people toward a deeper life in Christ and the sacraments.",
    },
    {
      title: "Christian formation",
      description:
        "Offer ongoing formation for the faithful so each person can grow in vocation, discipleship, and service to the Church.",
    },
    {
      title: "Christian pathways",
      description:
        "Use digital tools with discernment to connect people to trusted resources, meaningful next steps, and deeper communion.",
    },
  ],
  values: [
    {
      title: "Faith",
      description:
        "Trust God first, receive the Gospel personally, and let every initiative flow from communion with Jesus Christ.",
    },
    {
      title: "Hope",
      description:
        "Serve the Church with confidence that Christ is still drawing people to himself in every parish, family, and season.",
    },
    {
      title: "Love",
      description:
        "Build relationships marked by charity, accompaniment, and a real commitment to walk with people toward the Kingdom.",
    },
  ],
  featuredLinks: [
    {
      label: "Catholic.Work home",
      href: "https://catholic.work",
    },
    {
      label: "About Catholic.Work",
      href: "https://catholic.work/about/",
    },
    {
      label: "Barry P. Schoedel on LinkedIn",
      href: "https://www.linkedin.com/in/barrypschoedel/",
    },
  ],
  founder: {
    name: "Barry P. Schoedel",
    role: "Founder, instructional technologist, and Catholic ministry leader",
    bio: "Barry Schoedel brings experience in family evangelization, faith formation, instructional technology, and mission-driven digital strategy. This page positions Catholic.Work as a clear, credible apostolate led by a practitioner who bridges ministry, education, and technology.",
    profileHref: "https://www.linkedin.com/in/barrypschoedel/",
  },
  highlights: [
    "Mission-centered messaging drawn from Catholic.Work's apostolate framing",
    "A launch-ready single-page structure for a nonprofit or ministry website",
    "Clear pathways for families, parishes, dioceses, and supporters to engage",
  ],
  callsToAction: [
    {
      label: "Visit Catholic.Work",
      href: "https://catholic.work",
    },
    {
      label: "Read the about page",
      href: "https://catholic.work/about/",
    },
    {
      label: "Connect with Barry",
      href: "https://www.linkedin.com/in/barrypschoedel/",
    },
  ],
};

export const nonprofitSiteSources: NonprofitSiteSource[] = [catholicWorkSource];
