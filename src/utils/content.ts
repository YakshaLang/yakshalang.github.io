export interface ContentBadge {
	label: string;
	variant?: "primary" | "secondary" | "accent" | "neutral" | "info";
}

export function sortByFilename<T extends { file: string }>(items: T[]): T[] {
	return [...items].sort((a, b) => {
		const numA = parseInt(a.file.match(/(\d+)/)?.[1] ?? "0", 10);
		const numB = parseInt(b.file.match(/(\d+)/)?.[1] ?? "0", 10);
		return numA - numB;
	});
}

export function sortByDate<T extends { frontmatter: { pubDate?: string } }>(
	items: T[],
): T[] {
	return [...items].sort((a, b) => {
		const dateA = a.frontmatter.pubDate
			? new Date(a.frontmatter.pubDate).getTime()
			: 0;
		const dateB = b.frontmatter.pubDate
			? new Date(b.frontmatter.pubDate).getTime()
			: 0;
		return dateB - dateA;
	});
}

export function extractExcerpt(rawContent: string, maxLen = 160): string {
	const cleaned = rawContent
		.replace(/^import\s+.*$/gm, "")
		.replace(/^#+\s+.*$/gm, "")
		.replace(/<[^>]+>/g, "")
		.replace(/```[\s\S]*?```/g, "")
		.replace(/`[^`]+`/g, "")
		.replace(/^[-*]\s+.*$/gm, "")
		.replace(/\n{2,}/g, "\n")
		.trim();

	const paragraph = cleaned.split("\n").find((line) => line.trim().length > 0);
	if (!paragraph) return "";

	const text = paragraph.trim();
	if (text.length <= maxLen) return text;
	return `${text.slice(0, maxLen).trimEnd()}…`;
}

export function formatDate(pubDate: string): string {
	return new Date(pubDate).toLocaleDateString("en-US", {
		year: "numeric",
		month: "short",
		day: "numeric",
	});
}

export function getProposalNumber(file: string): string {
	const match = file.match(/(\d{4})/);
	return match ? match[1] : "";
}

export function getDemoBadges(frontmatter: {
	demoJs?: string;
	demoHtml?: string;
}): ContentBadge[] {
	const badges: ContentBadge[] = [];
	if (frontmatter.demoJs) {
		badges.push({ label: "Raylib", variant: "primary" });
		badges.push({ label: "WASM", variant: "secondary" });
	}
	if (frontmatter.demoHtml) {
		badges.push({ label: "WASM4", variant: "accent" });
	}
	return badges;
}
