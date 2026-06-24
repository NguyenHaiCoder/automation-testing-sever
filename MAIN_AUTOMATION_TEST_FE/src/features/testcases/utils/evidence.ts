import { logApi } from '@/features/logs';
import type { EvidenceImageRef, EvidenceRun, TestCase, TestResult } from '../types';

export interface ResolvedEvidenceImage {
  url: string;
  name: string;
}

export interface EvidenceRunGroup {
  runNumber: number;
  title: string;
  testDate: string;
  result: TestResult;
  images: ResolvedEvidenceImage[];
}

function resolveImageRefs(refs: EvidenceImageRef[]): ResolvedEvidenceImage[] {
  return refs
    .map((img, index) => {
      const url =
        img.url ??
        (img.runId && img.rel ? logApi.fileUrl(img.runId, img.rel) : '');
      const name = img.name ?? img.rel?.split('/').pop() ?? `Ảnh ${index + 1}`;
      return url ? { url, name } : null;
    })
    .filter((item): item is ResolvedEvidenceImage => item !== null);
}

export function resolveEvidenceRuns(testCase: TestCase): EvidenceRunGroup[] {
  if (testCase.evidenceRuns?.length) {
    return testCase.evidenceRuns.map((run) => ({
      runNumber: run.runNumber,
      title: `Kết quả ảnh minh chứng test lần ${run.runNumber}`,
      testDate: run.testDate,
      result: run.result,
      images: resolveImageRefs(run.images),
    }));
  }

  const flat = resolveEvidenceImages(testCase);
  if (!flat.length) return [];

  return [
    {
      runNumber: 1,
      title: 'Kết quả ảnh minh chứng test lần 1',
      testDate: testCase.testDate || '',
      result: testCase.result,
      images: flat,
    },
  ];
}

export function resolveEvidenceImages(testCase: TestCase): ResolvedEvidenceImage[] {
  if (testCase.evidenceImages?.length) {
    return resolveImageRefs(testCase.evidenceImages);
  }

  const raw = testCase.evidence?.trim();
  if (!raw) return [];

  return raw
    .split(/[\n,;]+/)
    .map((part) => part.trim())
    .filter((part) => part.startsWith('http') || part.startsWith('/api/'))
    .map((url, index) => ({ url, name: `Ảnh ${index + 1}` }));
}

export function countEvidenceImages(testCase: TestCase): number {
  return resolveEvidenceRuns(testCase).reduce((sum, run) => sum + run.images.length, 0);
}

export type { EvidenceRun };
