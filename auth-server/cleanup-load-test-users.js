/**
 * Cleanup script to delete load test users from auth-server database.
 *
 * This script:
 * 1. Finds all users with email pattern 'loadtest_user_%@example.com'
 * 2. Deletes their sessions (foreign key constraint)
 * 3. Deletes the users
 *
 * Usage:
 *   # Dry run (see what would be deleted)
 *   cd auth-server
 *   npm run cleanup:users -- --dry-run
 *
 *   # Actually delete
 *   npm run cleanup:users
 *
 * Or run directly:
 *   node cleanup-load-test-users.js --dry-run
 *   node cleanup-load-test-users.js
 */

import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function cleanupLoadTestUsers(dryRun = false) {
  try {
    console.log('🧹 Load Test User Cleanup');
    console.log('='.repeat(60));

    if (dryRun) {
      console.log('🔍 DRY RUN MODE - No data will be deleted\n');
    }

    // Find all load test users
    const loadTestUsers = await prisma.user.findMany({
      where: {
        email: {
          startsWith: 'loadtest_user_',
          endsWith: '@example.com'
        }
      },
      select: {
        id: true,
        email: true,
        name: true,
        createdAt: true,
        _count: {
          select: {
            sessions: true
          }
        }
      }
    });

    if (loadTestUsers.length === 0) {
      console.log('✓ No load test users found');
      return;
    }

    console.log(`Found ${loadTestUsers.length} load test users:`);
    console.log('');

    // Show summary
    let totalSessions = 0;
    loadTestUsers.slice(0, 5).forEach((user, index) => {
      console.log(`  ${index + 1}. ${user.email}`);
      console.log(`     ID: ${user.id}`);
      console.log(`     Sessions: ${user._count.sessions}`);
      console.log(`     Created: ${user.createdAt.toISOString()}`);
      totalSessions += user._count.sessions;
    });

    if (loadTestUsers.length > 5) {
      console.log(`  ... and ${loadTestUsers.length - 5} more users`);
      // Count remaining sessions
      loadTestUsers.slice(5).forEach(user => {
        totalSessions += user._count.sessions;
      });
    }

    console.log('');
    console.log('Will delete:');
    console.log(`  - ${loadTestUsers.length} users`);
    console.log(`  - ${totalSessions} sessions`);
    console.log('');

    if (dryRun) {
      console.log('✓ DRY RUN COMPLETE - No data was deleted');
      console.log('');
      console.log('To actually delete, run:');
      console.log('  node cleanup-load-test-users.js');
      return;
    }

    // Confirm deletion
    console.log('⚠️  This will permanently delete these users and their sessions!');
    console.log('   Press Ctrl+C to cancel, or press Enter to continue...');

    await new Promise((resolve) => {
      process.stdin.once('data', resolve);
    });

    console.log('');
    console.log('Deleting...');

    // Delete sessions first (foreign key constraint)
    const userIds = loadTestUsers.map(u => u.id);

    const deletedSessions = await prisma.session.deleteMany({
      where: {
        userId: {
          in: userIds
        }
      }
    });

    console.log(`✓ Deleted ${deletedSessions.count} sessions`);

    // Delete accounts
    const deletedAccounts = await prisma.account.deleteMany({
      where: {
        userId: {
          in: userIds
        }
      }
    });

    console.log(`✓ Deleted ${deletedAccounts.count} accounts`);

    // Delete verifications
    const deletedVerifications = await prisma.verification.deleteMany({
      where: {
        identifier: {
          in: loadTestUsers.map(u => u.email)
        }
      }
    });

    console.log(`✓ Deleted ${deletedVerifications.count} verifications`);

    // Delete users
    const deletedUsers = await prisma.user.deleteMany({
      where: {
        id: {
          in: userIds
        }
      }
    });

    console.log(`✓ Deleted ${deletedUsers.count} users`);

    console.log('='.repeat(60));
    console.log('🎉 Cleanup complete!');
    console.log(`   Users deleted: ${deletedUsers.count}`);
    console.log(`   Sessions deleted: ${deletedSessions.count}`);
    console.log(`   Accounts deleted: ${deletedAccounts.count}`);
    console.log(`   Verifications deleted: ${deletedVerifications.count}`);

  } catch (error) {
    console.error('❌ Error during cleanup:', error);
    throw error;
  } finally {
    await prisma.$disconnect();
  }
}

// Parse command line arguments
const args = process.argv.slice(2);
const dryRun = args.includes('--dry-run');

// Run cleanup
cleanupLoadTestUsers(dryRun)
  .catch((error) => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
