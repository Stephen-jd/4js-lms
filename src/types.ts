/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export interface Trainer {
  id: string;
  name: string;
  email: string;
  password?: string;
  subjects: string[];
  hourlyRate: number;
}

export type UKBoard = 'GCSE' | 'Edexcel' | 'AQA' | 'OCR' | 'Cambridge';

export interface ScheduleItem {
  id: string;
  trainerId: string;
  trainerName: string;
  dayOfWeek: string; // 'Monday', 'Tuesday', etc.
  startTime: string; // '16:30'
  endTime: string; // '18:00'
  subject: string; // 'Maths', 'Biology', etc.
  classYear: string; // 'Year 7', 'Year 12'
  description?: string; // 'Riaz maths', '(1:2)', etc.
}

export interface TimesheetEntry {
  id: string;
  trainerId: string;
  date: string; // 'YYYY-MM-DD'
  subject: string;
  startTime: string;
  endTime: string;
  hours: number;
  rate: number;
  totalPay: number;
  isCustom: boolean; // manually added vs auto-scheduled
}

export interface SyllabusTopic {
  id: string;
  board: UKBoard;
  year: string; // 'Year 7', 'Year 12', etc.
  subject: string; // 'Maths', 'Physics', etc.
  topic: string; // e.g., 'Quadratic Equations'
  subtopic: string; // e.g., 'Completing the Square'
  status: 'Not Started' | 'In Progress' | 'Completed';
  lastUpdated: string; // 'YYYY-MM-DD'
  coveredBy?: string; // Trainer Name
}

export interface ResourceItem {
  id: string;
  year: string; // 'Year 3' to 'Year 13'
  subject: string; // 'Maths', 'Physics', etc.
  topic: string;
  fileName: string;
  fileType: 'pdf' | 'docx' | 'pptx' | 'zip';
  driveUrl: string;
  weekNum: number;
  isCustom?: boolean;
}

export interface DashboardStats {
  totalFaculty: number;
  totalStudents: number;
  activeBatches: number;
  currentLiveLessons: Array<{
    subject: string;
    classYear: string;
    faculty: string;
    timeSlot: string;
  }>;
}
