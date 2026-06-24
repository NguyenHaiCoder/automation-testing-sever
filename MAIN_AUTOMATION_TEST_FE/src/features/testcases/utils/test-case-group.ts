import type { TestCase } from '../types';

export type TestCaseGroup = 'ADMIN' | 'OFFICER' | 'EMPLOYEE' | 'BR' | 'OTHER';

const GROUP_ORDER: TestCaseGroup[] = ['ADMIN', 'OFFICER', 'EMPLOYEE', 'BR', 'OTHER'];

export const TEST_CASE_GROUP_OPTIONS: { value: TestCaseGroup | 'all'; label: string }[] = [
  { value: 'all', label: 'Tất cả nhóm' },
  { value: 'ADMIN', label: 'ADMIN' },
  { value: 'OFFICER', label: 'OFFICER' },
  { value: 'EMPLOYEE', label: 'EMPLOYEE' },
  { value: 'BR', label: 'BR (Business Rule)' },
];

export function parseTestCaseGroup(testCase: TestCase): TestCaseGroup {
  const fromSection = testCase.section.match(/^\[(ADMIN|OFFICER|EMPLOYEE|BR)\]/);
  if (fromSection) return fromSection[1] as TestCaseGroup;

  const id = testCase.id.toUpperCase();
  if (id.startsWith('ADM-') || id.startsWith('CL-ADM')) return 'ADMIN';
  if (id.startsWith('OFF-') || id.startsWith('CL-OFF')) return 'OFFICER';
  if (id.startsWith('EMP-') || id.startsWith('CL-EMP')) return 'EMPLOYEE';
  if (id.startsWith('BR-') || id.startsWith('CL-BR')) return 'BR';
  return 'OTHER';
}

export function listGroupsInCases(cases: TestCase[]): TestCaseGroup[] {
  const set = new Set(cases.map(parseTestCaseGroup));
  return GROUP_ORDER.filter((g) => set.has(g));
}
