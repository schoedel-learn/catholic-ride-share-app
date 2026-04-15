export type NonprofitSiteSource = {
  slug: string;
  name: string;
  tagline: string;
  summary: string;
  mission: string;
  audience: string[];
  pillars: Array<{
    title: string;
    description: string;
  }>;
  highlights: string[];
  callsToAction: Array<{
    label: string;
    href: string;
  }>;
};

export const catholicWorkSource: NonprofitSiteSource = {
  slug: "catholic-work",
  name: "Catholic.Work",
  tagline: "Faith in action for justice and inclusive Catholic community.",
  summary:
    "A promotional website source for a nonprofit that invites Catholics to build inclusive communities, engage justice-focused ministry, and discover welcoming spiritual opportunities.",
  mission:
    "Catholic.Work encourages Catholics to turn faith into action by forming inclusive communities, sharing practical resources, and creating clear next steps for justice-centered participation.",
  audience: [
    "Catholics seeking a welcoming, justice-oriented community",
    "Supporters looking for faith-based advocacy and formation resources",
    "Partners, donors, and volunteers who want to strengthen inclusive ministry",
  ],
  pillars: [
    {
      title: "Inclusive community building",
      description:
        "Present the nonprofit as a welcoming home for Catholics who want prayer, belonging, and meaningful collaboration rooted in human dignity.",
    },
    {
      title: "Justice-focused formation",
      description:
        "Highlight educational resources, campaigns, and practical guidance that help visitors move from concern to action.",
    },
    {
      title: "Connection to opportunities",
      description:
        "Feature directories, events, and partner pathways that make it easier to join liturgies, programs, and service opportunities.",
    },
  ],
  highlights: [
    "Clear mission-led messaging for promotional and informational use",
    "A single-page structure suited for static hosting",
    "Flexible sections for programs, impact, partnerships, and donor outreach",
  ],
  callsToAction: [
    {
      label: "Visit Catholic.Work",
      href: "https://catholic.work",
    },
    {
      label: "Join the mission",
      href: "#get-involved",
    },
  ],
};

export const nonprofitSiteSources: NonprofitSiteSource[] = [catholicWorkSource];
