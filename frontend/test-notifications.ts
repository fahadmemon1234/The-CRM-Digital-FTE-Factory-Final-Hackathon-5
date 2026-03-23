/**
 * Test Notifications API Client
 * Run this to verify the notifications library is working
 */

import { getNotifications, getUnreadCount, markAllAsRead } from './src/lib/notifications';

async function testNotifications() {
  console.log('=== Testing Notifications API ===\n');

  try {
    // Test 1: Get unread count
    console.log('1. Testing unread count...');
    const unread = await getUnreadCount();
    console.log(`   ✓ Unread count: ${unread.unread}`);

    // Test 2: Get notifications
    console.log('\n2. Testing get notifications...');
    const notifications = await getNotifications(5, false);
    console.log(`   ✓ Total notifications: ${notifications.total}`);
    console.log(`   ✓ Unread in response: ${notifications.unread}`);
    console.log(`   ✓ Has more: ${notifications.has_more}`);
    
    if (notifications.notifications.length > 0) {
      console.log('\n   Latest notifications:');
      notifications.notifications.forEach((n, i) => {
        console.log(`   ${i + 1}. [${n.read ? '✓' : '🔔'}] ${n.title}`);
      });
    }

    // Test 3: Mark all as read (optional - commented out)
    // console.log('\n3. Testing mark all as read...');
    // const result = await markAllAsRead();
    // console.log(`   ✓ Marked ${result.updated_count} notifications as read`);

    console.log('\n✅ All tests passed!');
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
}

// Run the test
if (typeof window === 'undefined') {
  // Node.js environment
  testNotifications();
} else {
  // Browser environment
  window.addEventListener('load', () => {
    testNotifications();
  });
}
